import json
from src.fetchReports import (
    fetchAndSaveEvents,
    fetchAndSaveFights,
    fetchAndSaveReports,
    fetchFightsFromReport,
)
from src.enums import DifficultyType, KillType
from src.processEvents import createEncounterDataFrame, printPhaseTimeStatistics

if __name__ == "__main__":
    # fetchAndSaveReports(44, 100, 10)

    # fetchAndSaveFights(44, 3129, DifficultyType.Mythic, KillType.Encounters)
    # fetchAndSaveFights(44, 3131, DifficultyType.Mythic, KillType.Encounters)
    # fetchAndSaveFights(44, 3130, DifficultyType.Mythic, KillType.Encounters)

    # fetchAndSaveEvents(44, 3131, DifficultyType.Mythic)
    # fetchAndSaveEvents(44, 3129, DifficultyType.Mythic)
    # fetchAndSaveEvents(44, 3130, DifficultyType.Mythic)

    # fetchAndSaveReports(45, 100, 10)

    # fetchAndSaveFights(45, 62287, DifficultyType.Dungeon, KillType.Kills, False, 100)

    printPhaseTimeStatistics(createEncounterDataFrame(44, 3132, DifficultyType.Mythic))
