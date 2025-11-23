import json
import numpy as np
import pandas as pd
from collections import defaultdict
from dataclasses import dataclass, asdict
from scipy import stats
from statistics import mean, stdev
import matplotlib.pyplot as plt
from pathlib import Path
from tabulate import tabulate
from typing import List, Dict, Any, Optional, Tuple

from src.enums import DifficultyType
from src.utility import getEventsFilePath, getEventsFilePathForDungeon, getFightsFilePath, getTempPath


@dataclass
class PhaseTransition:
    id: int
    startTime: int


@dataclass
class PhaseAbilityTransition:
    abilityID: int
    abilityType: str
    castIndex: int


@dataclass
class Fight:
    code: str
    id: int
    startTime: int
    keystoneLevel: int | None
    phaseTransitions: List[PhaseTransition] | None


@dataclass
class Event:
    abilityID: int
    type: str
    fightCode: str
    fightID: int
    pullID: int
    timestamp: int
    sourceID: int
    targetID: int
    phase: int = 0
    phaseTime: float = 0.0
    totalTime: float = 0.0


def appendFightEvent(
    eventsFilePath: Path,
    allFightEvents: List[Event],
    phaseTransitions: List[PhaseTransition],
    fightCode: str,
    fightID: int,
    pullID: int = -1,
    phaseAbilities: List[PhaseAbilityTransition] = [],
):
    if eventsFilePath.exists():
        with open(eventsFilePath) as eventsFile:
            eventData = json.load(eventsFile)
            fightStartTime = eventData["startTime"]

            abilityPhaseTransitions: List[PhaseTransition] = []
            if len(phaseAbilities) > 0:
                abilityCounts = {}
                for event in eventData["events"]:
                    abilityID = event.get("abilityGameID")
                    eventType = event.get("type")
                    if abilityID not in abilityCounts:
                        abilityCounts[abilityID] = {}
                    if eventType not in abilityCounts[abilityID]:
                        abilityCounts[abilityID][eventType] = -1
                    abilityCounts[abilityID][eventType] += 1
                    for phaseAbility in phaseAbilities:
                        if (
                            abilityID == phaseAbility.abilityID
                            and eventType == phaseAbility.abilityType
                            and abilityCounts[abilityID][eventType] == phaseAbility.castIndex
                        ):
                            id = len(phaseTransitions) + len(abilityPhaseTransitions) + 1
                            startTime = event["timestamp"]
                            abilityPhaseTransitions.append(PhaseTransition(id=id, startTime=startTime))

            for event in eventData["events"]:
                if event.get("melee"):
                    continue

                phaseID = 1
                phaseStartTime = fightStartTime

                timestamp = event["timestamp"]
                for phaseTransition in phaseTransitions:
                    if timestamp >= phaseTransition.startTime:
                        phaseID = phaseTransition.id
                        phaseStartTime = phaseTransition.startTime
                    else:
                        break
                for abilityPhaseTransition in abilityPhaseTransitions:
                    if abilityPhaseTransition.startTime > phaseStartTime:
                        if timestamp >= abilityPhaseTransition.startTime:
                            phaseID = abilityPhaseTransition.id
                            phaseStartTime = abilityPhaseTransition.startTime

                allFightEvents.append(
                    Event(
                        timestamp=timestamp,
                        type=event["type"],
                        sourceID=event["sourceID"],
                        targetID=event["targetID"],
                        abilityID=event["abilityGameID"],
                        fightCode=fightCode,
                        fightID=fightID,
                        pullID=pullID,
                        totalTime=(timestamp - fightStartTime) / 1000.0,
                        phaseTime=(timestamp - phaseStartTime) / 1000.0,
                        phase=phaseID,
                    )
                )


def computeConfidenceInterval(data: pd.Series, confidence: float = 0.95) -> Tuple[float, float]:
    n = len(data)
    mean = np.mean(data)
    standardDeviation = np.std(data, ddof=1)  # sample std dev
    stderr = standardDeviation / np.sqrt(n)

    if n < 30:
        # Use t-distribution for small sample sizes
        tScore = stats.t.ppf((1.0 + confidence) / 2.0, df=n - 1)
        margin = tScore * stderr
    else:
        # Use z-distribution
        zScore = stats.norm.ppf((1.0 + confidence) / 2.0)
        margin = zScore * stderr

    return mean - margin, mean + margin


def plotAbilityCastTimes(phaseTimeStatistics: pd.DataFrame, abilityID: int, phase: int, type: str):
    subset = phaseTimeStatistics[
        (phaseTimeStatistics["phase"] == phase)
        & (phaseTimeStatistics["abilityID"] == abilityID)
        & (phaseTimeStatistics["type"] == type)
    ]

    plt.errorbar(
        subset["mean"],
        subset["castIndex"],
        xerr=subset["std"],
        fmt="o",  # circle marker
        ecolor="gray",  # error bar color
        elinewidth=2,
        capsize=4,  # little bar on end of error line
        label="Avg ± Std Dev",
    )

    plt.title(f"Ability: {abilityID} Phase: {phase} Type: {type}")
    plt.xlabel("Avg Cast Time (s)")
    plt.ylabel("Cast Index")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("buh.png")


def createEncounterDataFrame(
    zoneID: int,
    encounterID: int,
    difficulty: DifficultyType,
    dungeonEncounterID: int = 0,
    dropAbilities: List[int] = [],
    phaseAbilities: List[PhaseAbilityTransition] = [],
    ignorePhaseTransitions: bool = False,
    minPercentage: float = 100.0,
) -> pd.DataFrame:
    """Creates a Pandas DataFrame for the given encounter using all events matching the specified criteria.

    Args:
        zoneID (int): ZoneID used when fetching data.
        encounterID (int): Encounter ID of the boss encounter.
        difficulty (DifficultyType): Difficulty used when fetching data.
        dungeonEncounterID (int, optional): Encounter ID of the dungeon, if querying a dungeon boss.
        dropAbilities (List[int], optional): Ability IDs to drop from the data frame.
        phaseAbilities (List[PhaseAbilityTransition], optional): Replace phase transitions with transitions created at
        each ability entry.
        ignorePhaseTransitions (bool, optional): Whether to ignore phase transitions from WarcraftLogs API fights.
    Returns:
        pd.DataFrame: Empty if the fights file doesn't exist or if no fights were found.
    """

    if difficulty == DifficultyType.Dungeon:
        fightsFilePath = getFightsFilePath(zoneID, difficulty, dungeonEncounterID)
    else:
        fightsFilePath = getFightsFilePath(zoneID, difficulty, encounterID)

    if not fightsFilePath.exists():
        raise FileNotFoundError(f"The fights file path {zoneID}_{encounterID}_{difficulty}.json does not exist")

    with open(fightsFilePath) as fightsFile:
        fights = json.load(fightsFile)

    if not fights:
        raise LookupError(f"The fights file {zoneID}_{encounterID}_{difficulty}.json has not fights")

    allFightEvents: List[Event] = []

    for fightData in fights:
        startTime = fightData.get("startTime")
        if startTime == None:
            continue

        percentage = fightData.get("fightPercentage")
        if percentage:
            if percentage > minPercentage:
                continue

        fightCode = fightData["code"]
        fightID = fightData["id"]

        phaseTransitions: List[PhaseTransition] = []
        if difficulty == DifficultyType.Dungeon:
            filePaths = []
            dungeonPulls = fightData["dungeonPulls"]
            for pullID, pull in enumerate(dungeonPulls, start=1):
                if pull.get("encounterID") == encounterID:
                    eventsFilePath = getEventsFilePathForDungeon(
                        zoneID, dungeonEncounterID, encounterID, fightCode, fightID, pullID
                    )
                    phaseTransitions: List[PhaseTransition] = [PhaseTransition(id=1, startTime=pull["startTime"])]
                    appendFightEvent(
                        eventsFilePath, allFightEvents, phaseTransitions, fightCode, fightID, pullID, phaseAbilities
                    )
        else:
            if len(phaseAbilities) == 0 and ignorePhaseTransitions == False:
                rawPhaseTransitions = fightData.get("phaseTransitions")
                if not rawPhaseTransitions:
                    phaseTransitions = [PhaseTransition(id=1, startTime=fightData["startTime"])]
                else:
                    for normalizedPhaseNumber, phase in enumerate(
                        sorted(rawPhaseTransitions, key=lambda pt: pt["startTime"]), start=1
                    ):
                        phaseTransitions.append(PhaseTransition(id=normalizedPhaseNumber, startTime=phase["startTime"]))
            else:
                phaseTransitions: List[PhaseTransition] = [PhaseTransition(id=1, startTime=fightData["startTime"])]
            eventsFilePath = getEventsFilePath(zoneID, difficulty, encounterID, fightCode, fightID)
            appendFightEvent(eventsFilePath, allFightEvents, phaseTransitions, fightCode, fightID, -1, phaseAbilities)

    df = pd.DataFrame(allFightEvents)

    if df.empty:
        print("Empty dataframe")
        return df

    df.drop(df[df["abilityID"] == 145629].index, inplace=True)  # AMZ...

    cleaned = df.sort_values(["fightCode", "fightID", "pullID", "abilityID", "phase", "type", "phaseTime"])
    cleaned["castIndex"] = (
        cleaned.groupby(["fightCode", "fightID", "pullID", "abilityID", "phase", "type"]).cumcount() + 1
    )

    return cleaned


def aggregatePhaseTimeStatistics(dataFrame: pd.DataFrame, minCount: int = 0) -> pd.DataFrame:
    """Computes the count, mean, standard deviation, minimum, and maximum phaseTime values for a DataFrame describing
    an encounter.

    Args:
        dataFrame (pd.DataFrame): DataFrame returned by `createEncounterDataFrame`.
        minCount (int, optional): Throw out aggregated statistics where the count is less than this value.

    Returns:
        pd.DataFrame: A new DataFrame grouped by `abilityID`, `phase`, `type`, `castIndex`, aggregated across
        `phaseTime`.
    """
    grouped = dataFrame.groupby(["abilityID", "phase", "type", "castIndex"])
    filtered = grouped.filter(lambda g: len(g) >= minCount)

    phaseTimeStatistics = (
        filtered.groupby(["abilityID", "phase", "type", "castIndex"])["phaseTime"]
        .agg(count="count", mean="mean", std="std", min="min", max="max")
        .fillna(0)
        .reset_index()
    )
    return phaseTimeStatistics


def printPhaseTimeStatistics(
    dataFrame: pd.DataFrame,
    printAbilityUsage: bool = True,
    printDetailedCasts: bool = True,
    printAverageCastTimes: bool = True,
) -> None:
    """Prints various statistics using the passed DataFrame.

    Args:
        dataFrame (pd.DataFrame): DataFrame returned by `createEncounterDataFrame`.
        printAbilityUsage (bool, optional): Prints the total cast count of all abilities across all observed
        encounters. Defaults to True.
        printDetailedCasts (bool, optional): Prints aggregated phase time statistics. Defaults to True.
        printAverageCastTimes (bool, optional): Prints average cast times for abilities. Defaults to True.
    """

    phaseTimeStatistics = aggregatePhaseTimeStatistics(dataFrame)

    if printAbilityUsage:
        print("\n=== Ability Usage Across All Phases ===")
        for (abilityID, type), group in phaseTimeStatistics.groupby(["abilityID", "type"]):
            print(f"Ability {abilityID} {type}: used {group["castIndex"].nunique()} times")

    if printDetailedCasts:
        print("\n=== Detailed Cast Stats ===")
        for abilityID, abilityGroup in phaseTimeStatistics.groupby("abilityID"):
            print(f"\nAbility {abilityID}:")
            for phase, phaseGroup in abilityGroup.groupby("phase"):
                print(f"  Phase {phase}:")
                for type, typeGroup in phaseGroup.groupby("type"):
                    print(f"    Type {type}:")
                    if printDetailedCasts:
                        for _, row in typeGroup.iterrows():
                            print(
                                f"      Cast #{int(row['castIndex'])}: "
                                f"count={int(row['count'])}, "
                                f"avg={row['mean']:.1f}, "
                                f"std_dev={row['std']:.1f}, "
                                f"cv={row['std']/row['mean']:.1f}, "
                                f"min={row['min']:.1f}, "
                                f"max={row['max']:.1f}, "
                                f"max={row['max']:.1f}"
                            )

    if printAverageCastTimes:
        with open(getTempPath() / "AverageCastTimes.txt", "w") as averageCastTimesFile:
            for abilityID, abilityGroup in phaseTimeStatistics.groupby("abilityID"):
                for phase, phaseGroup in abilityGroup.groupby("phase"):
                    for cast_type, typeGroup in phaseGroup.groupby("type"):
                        typeGroupSorted = typeGroup.sort_values("castIndex")
                        df = pd.DataFrame(
                            {
                                "Count": typeGroupSorted["count"].astype(int).values,
                                "Mean": typeGroupSorted["mean"].values,
                                "Std Dev": typeGroupSorted["std"].values,
                            }
                        )
                        df["Avg Cast Time"] = df["Mean"].diff().fillna(df["Mean"])
                        df.drop(columns="Mean", inplace=True)
                        df.reset_index(drop=True, inplace=True)
                        averageCastTimesFile.write(f"\n| Ability {abilityID} - Phase {phase} - Type {cast_type} |\n")
                        data = [[row_name] + list(row) for row_name, row in df.T.iterrows()]
                        table_str = tabulate(data, tablefmt="github", showindex=False, floatfmt=".1f")
                        lines = table_str.splitlines()

                        # Replace Average Cast Time '|' with ","
                        averageCastTimeIndex = 3
                        lines[averageCastTimeIndex] = lines[averageCastTimeIndex].replace("|", ",")
                        lines[averageCastTimeIndex] = "|" + lines[averageCastTimeIndex].removeprefix(",")
                        lines[averageCastTimeIndex] = lines[averageCastTimeIndex].removesuffix(",") + "|"

                        averageCastTimesFile.write("\n".join(lines) + "\n")
