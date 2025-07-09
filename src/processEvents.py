import json
from statistics import mean, stdev

from src.enums import DifficultyType
from src.utility import getEventsPath, getFightsPath
from collections import defaultdict
from dataclasses import dataclass, asdict
from statistics import mean, stdev
from pathlib import Path
from typing import List, Dict, Any, Optional


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
    timestamp: int
    type: str
    sourceID: int
    targetID: int
    abilityID: int
    fightID: int

    totalTime: float = 0.0
    phaseTime: float = 0.0
    phase: int = 0


def findFight(fights: List[Dict[str, Any]], code: str) -> Optional[Dict[str, Any]]:
    for fight in fights:
        if fight["code"] == code:
            return fight
    return None


def getAbilityCasts(events: List[Event]) -> Dict[int, List[Event]]:
    castsByAbility: Dict[int, List[Event]] = defaultdict(list)
    for event in events:
        castsByAbility[event.abilityID].append(event)

    # Filter: prefer begincast over cast when both exist
    filteredCasts: Dict[int, List[Event]] = defaultdict(list)
    for abilityID, eventList in castsByAbility.items():
        for event in eventList:
            if event.type == "begincast":
                filteredCasts[abilityID].append(event)
    for abilityID, eventList in castsByAbility.items():
        for event in eventList:
            if event.type == "cast":
                if not filteredCasts[abilityID]:
                    filteredCasts[abilityID].append(event)
    return filteredCasts


def processEvents(zoneID: int, encounterID: int, difficulty: DifficultyType):
    fightsPath = getFightsPath() / f"{zoneID}_{encounterID}_{difficulty}.json"
    eventsDir = getEventsPath()

    with open(fightsPath) as fightsFile:
        fights = json.load(fightsFile)

    if not fights:
        print("No fights found.")
        return

    allFightEvents: List[List[Event]] = []

    for fightData in fights:
        if not fightData["phaseTransitions"]:
            continue
        phaseTransitions = [
            PhaseTransition(id=phaseTransition["id"], startTime=phaseTransition["startTime"])
            for phaseTransition in sorted(
                fightData.get("phaseTransitions", []), key=lambda phaseTransition: phaseTransition["startTime"]
            )
        ]

        fightCode = fightData["code"]
        fightID = fightData["id"]

        eventsPath = eventsDir / f"{zoneID}_{encounterID}_{difficulty}_{fightCode}_{fightID}.json"
        with open(eventsPath) as eventsFile:
            eventData = json.load(eventsFile)
            fightStartTime = eventData["startTime"]

            events: List[Event] = []
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

                events.append(
                    Event(
                        timestamp=timestamp,
                        type=event["type"],
                        sourceID=event["sourceID"],
                        targetID=event["targetID"],
                        abilityID=event["abilityGameID"],
                        fightID=fightID,
                        totalTime=(timestamp - fightStartTime) / 1000.0,
                        phaseTime=(timestamp - phaseStartTime) / 1000.0,
                        phase=phaseID,
                    )
                )

            allFightEvents.append(events)

    # Save processed events for debugging
    outputPath = eventsDir / f"{zoneID}_{encounterID}_{difficulty}_total.json"
    with open(outputPath, "w") as outFile:
        json.dump(
            [[asdict(event) for event in events] for events in allFightEvents],
            outFile,
            indent=2,
        )

    # Analyze timings
    analyzeCastTimings(allFightEvents)


def analyzeCastTimings(allFightEvents: List[List[Event]]):
    abilityTimings: Dict[int, List[Dict[str, Any]]] = defaultdict(list)

    for fightIndex, events in enumerate(allFightEvents):
        abilityCasts = getAbilityCasts(events)

        for abilityID, abilityInstancesByCastIndex in abilityCasts.items():
            # Group by phase
            phaseGroups: Dict[int, List[Event]] = defaultdict(list)
            for cast in abilityInstancesByCastIndex:
                phaseGroups[cast.phase].append(cast)

            for phase, phaseCasts in phaseGroups.items():
                phaseCasts.sort(key=lambda phaseCast: phaseCast.phaseTime)
                for castIndex, cast in enumerate(phaseCasts, start=1):
                    abilityTimings[abilityID].append(
                        {
                            "castIndex": castIndex,
                            "phaseTime": cast.phaseTime,
                            "phase": phase,
                        }
                    )

    print("\n=== Ability Usage ===")
    for abilityID, timings in abilityTimings.items():
        print(f"Ability {abilityID}: used {len(timings)} times")

    castTimeBuckets: Dict[int, Dict[int, Dict[int, List[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    # {abilityID: {phase: {castIndex: [phaseTimes]}}}

    for abilityID, abilityInstances in abilityTimings.items():
        for abilityInstance in abilityInstances:
            castTimeBuckets[abilityID][abilityInstance["phase"]][abilityInstance["castIndex"]].append(
                abilityInstance["phaseTime"]
            )

    print("\n=== Detailed Cast Stats ===")
    for abilityID, abilityInstancesByPhase in castTimeBuckets.items():
        print(f"\nAbility {abilityID}:")
        for phase, abilityInstancesByCastIndex in sorted(abilityInstancesByPhase.items()):
            print(f"  Phase {phase}:")
            for castIndex, phaseTimes in sorted(abilityInstancesByCastIndex.items()):
                averagePhaseTime = mean(phaseTimes)
                count = len(phaseTimes)
                standardDeviation = stdev(phaseTimes) if count > 1 else 0.0
                print(
                    f"    Cast #{castIndex}: count={count}, avg={averagePhaseTime:.2f}, "
                    f"std_dev={standardDeviation:.2f}, min={min(phaseTimes):.2f}, max={max(phaseTimes):.2f}"
                )
            castIndices = sorted(abilityInstancesByCastIndex.keys())
            if len(castIndices) < 2:
                continue  # Need at least 2 casts to get an interval

            # Collect average times in order
            averageCastTimes = []
            for castIndex in castIndices:
                phaseTimes = abilityInstancesByCastIndex[castIndex]
                averagePhaseTime = mean(phaseTimes)
                averageCastTimes.append(averagePhaseTime)

            # Compute intervals between consecutive casts
            intervals = [averageCastTimes[i + 1] - averageCastTimes[i] for i in range(len(averageCastTimes) - 1)]

            averageInterval = mean(intervals)
            standardDeviationInterval = stdev(intervals) if len(intervals) > 1 else 0.0

            print(
                f"  Phase {phase}: estimated cast interval ≈ {averageInterval:.2f}s "
                + f"(std dev: {standardDeviationInterval:.2f}s)"
            )
