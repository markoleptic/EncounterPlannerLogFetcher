import json
from src.fetchReports import (
    fetchAndSaveEvents,
    fetchAndSaveEventsForDungeon,
    fetchAndSaveFights,
    fetchAndSaveFightsForDungeon,
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

    # fetchAndSaveFightsForDungeon(45, 62287)
    # fetchAndSaveEventsForDungeon(45, 2403, 62287)
    fetchAndSaveEventsForDungeon(45, 2380, 62287, True)
    fetchAndSaveEventsForDungeon(45, 2381, 62287, True)
    fetchAndSaveEventsForDungeon(45, 2401, 62287, True)
    fetchAndSaveEventsForDungeon(45, 2403, 62287, True)
    # df = createEncounterDataFrame(44, 3122, DifficultyType.Mythic)
    # printPhaseTimeStatistics(df, True, False)
