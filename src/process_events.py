import json
from statistics import mean, stdev

from src.enums import DifficultyType
from src.utility import get_events_path, get_fights_path
from collections import defaultdict
from dataclasses import dataclass, asdict
from statistics import mean, stdev
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class PhaseTransition:
    id: int
    start_time: int


@dataclass
class Fight:
    code: str
    id: int
    start_time: int
    keystone_level: int | None
    phase_transitions: List[PhaseTransition] | None


@dataclass
class Event:
    timestamp: int
    type: str
    source_id: int
    target_id: int
    ability_id: int
    fight_id: int

    total_time: float = 0.0
    phase_time: float = 0.0
    phase: int = 0


def find_fight(fights: List[Dict[str, Any]], code: str) -> Optional[Dict[str, Any]]:
    for fight in fights:
        if fight["code"] == code:
            return fight
    return None


def get_ability_casts(events: List[Event]) -> Dict[int, List[Event]]:
    casts_by_ability: Dict[int, List[Event]] = defaultdict(list)
    for event in events:
        casts_by_ability[event.ability_id].append(event)

    # Filter: prefer begincast over cast when both exist
    filtered_casts: Dict[int, List[Event]] = defaultdict(list)
    for ability_id, evs in casts_by_ability.items():
        for e in evs:
            if e.type == "begincast":
                filtered_casts[ability_id].append(e)
            elif e.type == "cast":
                if not any(be.total_time == e.total_time for be in filtered_casts[ability_id]):
                    filtered_casts[ability_id].append(e)
    return filtered_casts


def process_events(zone_id: int, encounter_id: int, difficulty: DifficultyType):
    fights_path = get_fights_path() / f"{zone_id}_{encounter_id}_{difficulty}.json"
    events_dir = get_events_path()

    with open(fights_path) as fights_file:
        fights = json.load(fights_file)

    if not fights:
        print("No fights found.")
        return

    all_fight_events: List[List[Event]] = []

    for fight_data in fights:
        if not fight_data["phase_transitions"]:
            continue
        phase_transitions = [
            PhaseTransition(id=pt["id"], start_time=pt["startTime"])
            for pt in sorted(fight_data.get("phase_transitions", []), key=lambda p: p["startTime"])
        ]

        fight_code = fight_data["code"]
        fight_id = fight_data["id"]

        events_path = events_dir / f"{zone_id}_{encounter_id}_{difficulty}_{fight_code}_{fight_id}.json"
        with open(events_path) as events_file:
            event_data = json.load(events_file)
            fight_start_time = event_data["start_time"]

            events: List[Event] = []
            for e in event_data["events"]:
                timestamp = e["timestamp"]

                # Determine phase
                phase_id = 0
                phase_start_time = fight_start_time
                for pt in phase_transitions:
                    if timestamp >= pt.start_time:
                        phase_id = pt.id
                        phase_start_time = pt.start_time
                    else:
                        break

                events.append(
                    Event(
                        timestamp=timestamp,
                        type=e["type"],
                        source_id=e["sourceID"],
                        target_id=e["targetID"],
                        ability_id=e["abilityGameID"],
                        fight_id=fight_id,
                        total_time=(timestamp - fight_start_time) / 1000.0,
                        phase_time=(timestamp - phase_start_time) / 1000.0,
                        phase=phase_id,
                    )
                )

            all_fight_events.append(events)

    # Save processed events for debugging
    output_path = events_dir / f"{zone_id}_{encounter_id}_{difficulty}_total.json"
    with open(output_path, "w") as out_file:
        json.dump(
            [[asdict(e) for e in events] for events in all_fight_events],
            out_file,
            indent=2,
        )

    # Analyze timings
    analyze_cast_timings(all_fight_events)


def analyze_cast_timings(all_fight_events: List[List[Event]]):
    ability_timings: Dict[int, List[Dict[str, Any]]] = defaultdict(list)

    for fight_index, events in enumerate(all_fight_events):
        ability_casts = get_ability_casts(events)

        for ability_id, casts in ability_casts.items():
            # Group by phase
            phase_groups: Dict[int, List[Event]] = defaultdict(list)
            for e in casts:
                phase_groups[e.phase].append(e)

            for phase, phase_casts in phase_groups.items():
                phase_casts.sort(key=lambda e: e.phase_time)
                for cast_idx, e in enumerate(phase_casts, start=1):
                    ability_timings[ability_id].append(
                        {
                            "fight_index": fight_index,
                            "cast_index": cast_idx,
                            "phase_time": e.phase_time,
                            "phase": phase,
                        }
                    )

    print("\n=== Ability Usage ===")
    for ability_id, timings in ability_timings.items():
        print(f"Ability {ability_id}: used {len(timings)} times")

    cast_time_buckets: Dict[int, Dict[int, Dict[int, List[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    # {ability_id: {phase: {cast_index: [phase_times]}}}

    for ability_id, timings in ability_timings.items():
        for t in timings:
            cast_time_buckets[ability_id][t["phase"]][t["cast_index"]].append(t["phase_time"])

    print("\n=== Detailed Cast Stats ===")
    for ability_id, phase_data in cast_time_buckets.items():
        print(f"\nAbility {ability_id}:")
        for phase, casts in sorted(phase_data.items()):
            print(f"  Phase {phase}:")
            for cast_index, times in sorted(casts.items()):
                avg_time = mean(times)
                count = len(times)
                std_dev = stdev(times) if count > 1 else 0.0
                print(
                    f"    Cast #{cast_index}: count={count}, avg={avg_time:.2f}, "
                    f"std_dev={std_dev:.2f}, min={min(times):.2f}, max={max(times):.2f}"
                )
