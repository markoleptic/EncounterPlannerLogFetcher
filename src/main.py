import json
from src.fetchReports import (
    fetchAndSaveEvents,
    fetchAndSaveFights,
    fetchAndSaveReports,
)
from src.enums import DifficultyType, KillType
from src.processEvents import processEvents

if __name__ == "__main__":
    processEvents(44, 3132, DifficultyType.Heroic)
    # fetch_and_save_reports(44, 100, 10)
    # fetch_and_save_fights(44, 3132, DifficultyType.Heroic, KillType.Kills, 100, 10)
    # fetch_and_save_events(44, 3132, DifficultyType.Heroic)
