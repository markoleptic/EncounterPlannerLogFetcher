import json
import numpy as np
import pandas as pd
from collections import defaultdict
from dataclasses import dataclass, asdict
from statistics import mean, stdev
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.enums import DifficultyType
from src.utility import getEventsFilePath, getFightsFilePath


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
    fightID: int
    fightCode: str
    timestamp: int
    sourceID: int
    targetID: int
    phase: int = 0
    phaseTime: float = 0.0
    totalTime: float = 0.0


def createEncounterDataFrame(zoneID: int, encounterID: int, difficulty: DifficultyType) -> pd.DataFrame:
    """Creates a Pandas DataFrame for the given encounter using all events events matching the specified criteria.

    Args:
        zoneID (int): ZoneID used when fetching data.
        encounterID (int): Encounter ID of the boss encounter.
        difficulty (DifficultyType): Difficulty used when fetching data.

    Returns:
        pd.DataFrame: Empty if the fights file doesn't exist or if no fights were found.
    """
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

        eventsFilePath = getEventsFilePath(zoneID, difficulty, encounterID, fightCode, fightID)
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
                            fightID=fightID,
                            fightCode=fightCode,
                            totalTime=(timestamp - fightStartTime) / 1000.0,
                            phaseTime=(timestamp - phaseStartTime) / 1000.0,
                            phase=phaseID,
                        )
                    )

    df = pd.DataFrame(allFightEvents)

    if df.empty:
        print("Empty dataframe")
        return df

    df.drop(df[df["abilityID"] == 145629].index, inplace=True)  # AMZ...

    # Sort by fight, ability, then timestamp
    df = df.sort_values(["fightCode", "fightID", "abilityID", "timestamp"])

    # Within each fightCode+fightID+abilityID, shift the 'type' column so we can compare each row to its predecessor
    df["prev_type"] = df.groupby(["fightCode", "fightID", "abilityID"])["type"].shift(1)

    # Drop any 'cast' whose previous event was a 'begincast'
    mask = (df["type"] == "cast") & (df["prev_type"] == "begincast")
    cleaned = df[~mask].copy()

    # Recompute castIndex
    cleaned["castIndex"] = (
        cleaned.sort_values(["fightCode", "fightID", "abilityID", "phase", "phaseTime"])
        .groupby(["fightCode", "fightID", "abilityID", "phase"])
        .cumcount()
        + 1
    )

    # Drop the helper column
    cleaned = cleaned.drop(columns="prev_type")

    return cleaned


def aggregatePhaseTimeStatistics(dataFrame: pd.DataFrame) -> pd.DataFrame:
    """Computes the count, mean, standard deviation, minimum, and maximum phaseTime values for a DataFrame describing
    an encounter.

    Args:
        dataFrame (pd.DataFrame): DataFrame returned by `createEncounterDataFrame`.

    Returns:
        pd.DataFrame: A new DataFrame grouped by `abilityID`, `phase`, `castIndex`, aggregated across `phaseTime`.
    """
    phaseTimeStatistics = (
        dataFrame.groupby(["abilityID", "phase", "castIndex"])["phaseTime"]
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

    print("\n=== Ability Usage ===")
    usage = phaseTimeStatistics.groupby("abilityID").size().sort_index()
    for abilityID, count in usage.items():
        print(f"Ability {abilityID}: used {count} times")

    # --- 2) Detailed Cast Stats + estimated interval ---
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
            castMeans: np.ndarray = phaseStatistics["mean"].to_numpy()
            if len(castMeans) > 1:
                intervals = castMeans[1:] - castMeans[:-1]
                averageInterval = intervals.mean()
                stdInterval = intervals.std()
                print(
                    f"  Phase {phase}: estimated cast interval ≈ {averageInterval:.2f}s (std dev: {stdInterval:.2f}s)"
                )

    print("\n=== Average Cast Times Lists ===")
    for (abilityID, phase), grp in phaseTimeStatistics.groupby(["abilityID", "phase"]):
        meanCastTimes = grp.sort_values("castIndex")["mean"].to_numpy()
        relativeTimes = np.insert(np.diff(meanCastTimes), 0, meanCastTimes[0])
        relativeTimes = np.round(relativeTimes, 2)
        print(
            f"{abilityID}:{phase}: {np.array2string(meanCastTimes, precision=2, separator=', ', floatmode='fixed', 
                                                    max_line_width=9999)}"
        )
