import json
from src.fetch_reports import (
    fetch_and_save_events,
    fetch_and_save_fights,
    fetch_and_save_reports,
)
from src.enums import DifficultyType, KillType
from src.process_events import process_events

if __name__ == "__main__":
    process_events(44, 3132, DifficultyType.Heroic)
    # fetch_and_save_reports(44, 100, 10)
    # fetch_and_save_fights(44, 3132, DifficultyType.Heroic, KillType.Kills, 100, 10)
    # fetch_and_save_events(44, 3132, DifficultyType.Heroic)
