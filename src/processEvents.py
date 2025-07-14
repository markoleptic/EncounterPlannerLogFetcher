import json
import numpy as np
import pandas as pd
from collections import defaultdict
from dataclasses import dataclass, asdict
from statistics import mean, stdev
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.enums import DifficultyType
from src.utility import getEventsFilePath, getEventsFilePathForDungeon, getFightsFilePath


@dataclass
class PhaseTransition:
    id: int
    startTime: int


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
):
    if eventsFilePath.exists():
        with open(eventsFilePath) as eventsFile:
            eventData = json.load(eventsFile)
            fightStartTime = eventData["startTime"]

            for event in eventData["events"]:
                timestamp = event["timestamp"]

                # Determine phase
                phaseID = 0
                phaseStartTime = fightStartTime
                for phaseTransition in phaseTransitions:
                    if timestamp >= phaseTransition.startTime:
                        phaseID = phaseTransition.id
                        phaseStartTime = phaseTransition.startTime
                    else:
                        break
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


def createEncounterDataFrame(
    zoneID: int, encounterID: int, difficulty: DifficultyType, dungeonEncounterID: int = 0
) -> pd.DataFrame:
    """Creates a Pandas DataFrame for the given encounter using all events events matching the specified criteria.

    Args:
        zoneID (int): ZoneID used when fetching data.
        encounterID (int): Encounter ID of the boss encounter.
        difficulty (DifficultyType): Difficulty used when fetching data.
        dungeonEncounterID (int, optional): Encounter ID of the dungeon, if querying a dungeon boss.

    Returns:
        pd.DataFrame: Empty if the fights file doesn't exist or if no fights were found.
    """
    if difficulty == DifficultyType.Dungeon:
        fightsFilePath = getFightsFilePath(zoneID, difficulty, dungeonEncounterID)
    else:
        fightsFilePath = getFightsFilePath(zoneID, difficulty, encounterID)

    if not fightsFilePath.exists():
        print(f"{zoneID}_{encounterID}_{difficulty}.json does not exist")
        return pd.DataFrame()

    with open(fightsFilePath) as fightsFile:
        fights = json.load(fightsFile)

    if not fights:
        print("No fights found")
        return pd.DataFrame()

    allFightEvents: List[Event] = []

    for fightData in fights:
        startTime = fightData.get("startTime")
        if startTime == None:
            continue

        rawPhaseTransitions = fightData.get("phaseTransitions") or []
        # if no real transitions, assume one phase starting at the very beginning
        if not rawPhaseTransitions:
            rawPhaseTransitions = [{"id": 0, "startTime": fightData["startTime"]}]

        phaseTransitions: List[PhaseTransition] = []
        for normalizedPhaseNumber, phase in enumerate(
            sorted(rawPhaseTransitions, key=lambda pt: pt["startTime"]), start=1
        ):
            phaseTransitions.append(PhaseTransition(id=normalizedPhaseNumber, startTime=phase["startTime"]))

        fightCode = fightData["code"]
        fightID = fightData["id"]

        if difficulty == DifficultyType.Dungeon:
            filePaths = []
            dungeonPulls = fightData["dungeonPulls"]
            for pullID, pull in enumerate(dungeonPulls, start=1):
                if pull.get("encounterID") == encounterID:
                    eventsFilePath = getEventsFilePathForDungeon(
                        zoneID, dungeonEncounterID, encounterID, fightCode, fightID, pullID
                    )
                    appendFightEvent(eventsFilePath, allFightEvents, phaseTransitions, fightCode, fightID, pullID)
        else:
            eventsFilePath = getEventsFilePath(zoneID, difficulty, encounterID, fightCode, fightID)
            appendFightEvent(eventsFilePath, allFightEvents, phaseTransitions, fightCode, fightID)

    df = pd.DataFrame(allFightEvents)

    if df.empty:
        print("Empty dataframe")
        return df

    df.drop(df[df["abilityID"] == 145629].index, inplace=True)  # AMZ...

    castsDf = df[df["type"].isin(["begincast", "cast"])].copy()
    othersDf = df[~df["type"].isin(["begincast", "cast"])].copy()

    castsDf = castsDf.sort_values(["fightCode", "fightID", "pullID", "abilityID", "timestamp"])

    # Shift the 'type' column so we can compare each row to its predecessor
    castsDf["prevType"] = castsDf.groupby(["fightCode", "fightID", "pullID", "abilityID"])["type"].shift(1)

    # Drop 'cast' whose previous is 'begincast'
    mask = (castsDf["type"] == "cast") & (castsDf["prevType"] == "begincast")
    castsDf = castsDf[~mask].copy()

    # Merge remaining 'cast'
    castsDf["type"] = castsDf["type"].replace("cast", "begincast")

    # Drop helper column
    castsDf.drop(columns="prevType", inplace=True)

    # Combine back with the other events
    cleaned = pd.concat([castsDf, othersDf], ignore_index=True)

    cleaned = cleaned.sort_values(["fightCode", "fightID", "pullID", "abilityID", "phase", "phaseTime"])
    cleaned["castIndex"] = cleaned.groupby(["fightCode", "fightID", "pullID", "abilityID", "phase"]).cumcount() + 1

    return cleaned


def aggregatePhaseTimeStatistics(dataFrame: pd.DataFrame) -> pd.DataFrame:
    """Computes the count, mean, standard deviation, minimum, and maximum phaseTime values for a DataFrame describing
    an encounter.

    Args:
        dataFrame (pd.DataFrame): DataFrame returned by `createEncounterDataFrame`.

    Returns:
        pd.DataFrame: A new DataFrame grouped by `abilityID`, `phase`, `type`, `castIndex`, aggregated across
        `phaseTime`.
    """
    phaseTimeStatistics = (
        dataFrame.groupby(["abilityID", "phase", "type", "castIndex"])["phaseTime"]
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
        print("\n=== Ability Usage ===")
        usage = phaseTimeStatistics.groupby("abilityID").size().sort_index()
        for abilityID, count in usage.items():
            print(f"Ability {abilityID}: used {count} times")

    # --- 2) Detailed Cast Stats + estimated interval ---
    if printDetailedCasts:
        print("\n=== Detailed Cast Stats ===")
        uniqueAbilityIDs: List[int] = sorted(phaseTimeStatistics["abilityID"].unique())
        for abilityID in uniqueAbilityIDs:
            print(f"\nAbility {abilityID}:")
            abilityStatistics: pd.DataFrame = phaseTimeStatistics[phaseTimeStatistics["abilityID"] == abilityID]
            uniquePhases: List[int] = sorted(abilityStatistics["phase"].unique())
            for phase in uniquePhases:
                print(f"  Phase {phase}:")
                phaseStatistics: pd.DataFrame = abilityStatistics[abilityStatistics["phase"] == phase].sort_values(
                    "castIndex"
                )
                for _, row in phaseStatistics.iterrows():
                    print(
                        f"    Cast #{int(row['castIndex'])}: "
                        f"count={int(row['count'])}, "
                        f"avg={row['mean']:.2f}, "
                        f"std_dev={row['std']:.2f}, "
                        f"min={row['min']:.2f}, "
                        f"max={row['max']:.2f}"
                    )
                # Compute interval if there’s more than one cast
                # castMeans: np.ndarray = phaseStatistics["mean"].to_numpy()
                # if len(castMeans) > 1:
                #     intervals = castMeans[1:] - castMeans[:-1]
                #     averageInterval = intervals.mean()
                #     stdInterval = intervals.std()
                #     print(f"    Estimated cast interval ≈ {averageInterval:.2f}s (std dev: {stdInterval:.2f}s)")

    if printAverageCastTimes:
        print("\n=== Average Cast Times Lists ===")
        for (abilityID, phase), grp in phaseTimeStatistics.groupby(["abilityID", "phase"]):
            meanCastTimes = grp.sort_values("castIndex")["mean"].to_numpy()
            relativeTimes = np.insert(np.diff(meanCastTimes), 0, meanCastTimes[0])
            formatted = ", ".join(f"{v:.2f}" for v in relativeTimes)
            print(f"{abilityID}:{phase}: {formatted}")
