import json
import time
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

    # fetchAndSaveFightsForDungeon(45, 112442)
    # fetchAndSaveFightsForDungeon(45, 112441)

    # fetchAndSaveEventsForDungeon(45, 3107, 12830)
    # fetchAndSaveEventsForDungeon(45, 3108, 12830)
    # fetchAndSaveEventsForDungeon(45, 3109, 12830)

    # fetchAndSaveEventsForDungeon(45, 2419, 112442)
    # fetchAndSaveEventsForDungeon(45, 2426, 112442)
    # fetchAndSaveEventsForDungeon(45, 2442, 112442)

    # fetchAndSaveEventsForDungeon(45, 2424, 112441)
    # fetchAndSaveEventsForDungeon(45, 2425, 112441)
    # fetchAndSaveEventsForDungeon(45, 2437, 112441)
    # fetchAndSaveEventsForDungeon(45, 2440, 112441)
    # fetchAndSaveEventsForDungeon(45, 2441, 112441)

    fetchAndSaveFightsForDungeon(45, 62649)
    fetchAndSaveFightsForDungeon(45, 62662)
    fetchAndSaveFightsForDungeon(45, 62773)
    fetchAndSaveFightsForDungeon(45, 62660)

    fetchAndSaveEventsForDungeon(45, 2835, 62649)
    fetchAndSaveEventsForDungeon(45, 2847, 62649)
    fetchAndSaveEventsForDungeon(45, 2848, 62649)

    fetchAndSaveEventsForDungeon(45, 2837, 62662)
    fetchAndSaveEventsForDungeon(45, 2838, 62662)
    fetchAndSaveEventsForDungeon(45, 2839, 62662)

    fetchAndSaveEventsForDungeon(45, 3019, 62773)
    fetchAndSaveEventsForDungeon(45, 3020, 62773)
    fetchAndSaveEventsForDungeon(45, 3053, 62773)

    fetchAndSaveEventsForDungeon(45, 2901, 62660)
    fetchAndSaveEventsForDungeon(45, 2906, 62660)
    fetchAndSaveEventsForDungeon(45, 2926, 62660)

    # df = createEncounterDataFrame(45, 2403, DifficultyType.Dungeon, 62287)
    # printPhaseTimeStatistics(df, True, False)
