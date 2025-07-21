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
from src.processEvents import PhaseAbilityTransition, createEncounterDataFrame, printPhaseTimeStatistics
from src.utility import getReportsPath


def fetchAndSaveFightsAndEventsForManaforgeOmegaMythic():
    fetchAndSaveFights(44, 3129, DifficultyType.Mythic, KillType.Encounters)
    fetchAndSaveFights(44, 3131, DifficultyType.Mythic, KillType.Encounters)
    fetchAndSaveFights(44, 3130, DifficultyType.Mythic, KillType.Encounters)
    fetchAndSaveFights(44, 3132, DifficultyType.Mythic, KillType.Encounters)
    fetchAndSaveFights(44, 3122, DifficultyType.Mythic, KillType.Encounters)
    fetchAndSaveFights(44, 3133, DifficultyType.Mythic, KillType.Encounters)
    fetchAndSaveFights(44, 3134, DifficultyType.Mythic, KillType.Encounters)

    fetchAndSaveEvents(44, 3129, DifficultyType.Mythic)
    fetchAndSaveEvents(44, 3131, DifficultyType.Mythic)
    fetchAndSaveEvents(44, 3130, DifficultyType.Mythic)
    fetchAndSaveEvents(44, 3132, DifficultyType.Mythic)
    fetchAndSaveEvents(44, 3122, DifficultyType.Mythic)
    fetchAndSaveEvents(44, 3133, DifficultyType.Mythic)
    fetchAndSaveEvents(44, 3134, DifficultyType.Mythic)


def fetchAndSaveFightsAndEventsForManaforgeOmegaHeroic():
    fetchAndSaveFights(44, 3129, DifficultyType.Heroic, KillType.Encounters)
    fetchAndSaveFights(44, 3131, DifficultyType.Heroic, KillType.Encounters)
    fetchAndSaveFights(44, 3130, DifficultyType.Heroic, KillType.Encounters)
    fetchAndSaveFights(44, 3132, DifficultyType.Heroic, KillType.Encounters)
    fetchAndSaveFights(44, 3122, DifficultyType.Heroic, KillType.Encounters)
    fetchAndSaveFights(44, 3133, DifficultyType.Heroic, KillType.Encounters)
    fetchAndSaveFights(44, 3134, DifficultyType.Heroic, KillType.Encounters)

    fetchAndSaveEvents(44, 3129, DifficultyType.Heroic)
    fetchAndSaveEvents(44, 3131, DifficultyType.Heroic)
    fetchAndSaveEvents(44, 3130, DifficultyType.Heroic)
    fetchAndSaveEvents(44, 3132, DifficultyType.Heroic)
    fetchAndSaveEvents(44, 3122, DifficultyType.Heroic)
    fetchAndSaveEvents(44, 3133, DifficultyType.Heroic)
    fetchAndSaveEvents(44, 3134, DifficultyType.Heroic)


def fetchAndSaveFightsAndEventsForSeason3Dungeons():
    fetchAndSaveFightsForDungeon(45, 12830)
    fetchAndSaveFightsForDungeon(45, 62287)
    fetchAndSaveFightsForDungeon(45, 62649)
    fetchAndSaveFightsForDungeon(45, 62660)
    fetchAndSaveFightsForDungeon(45, 62662)
    fetchAndSaveFightsForDungeon(45, 62773)
    fetchAndSaveFightsForDungeon(45, 112441)
    fetchAndSaveFightsForDungeon(45, 112442)

    fetchAndSaveEventsForDungeon(45, 3107, 12830)
    fetchAndSaveEventsForDungeon(45, 3108, 12830)
    fetchAndSaveEventsForDungeon(45, 3109, 12830)

    fetchAndSaveEventsForDungeon(45, 2380, 62287)
    fetchAndSaveEventsForDungeon(45, 2381, 62287)
    fetchAndSaveEventsForDungeon(45, 2401, 62287)
    fetchAndSaveEventsForDungeon(45, 2403, 62287)

    fetchAndSaveEventsForDungeon(45, 2835, 62649)
    fetchAndSaveEventsForDungeon(45, 2847, 62649)
    fetchAndSaveEventsForDungeon(45, 2848, 62649)

    fetchAndSaveEventsForDungeon(45, 2901, 62660)
    fetchAndSaveEventsForDungeon(45, 2906, 62660)
    fetchAndSaveEventsForDungeon(45, 2926, 62660)

    fetchAndSaveEventsForDungeon(45, 2837, 62662)
    fetchAndSaveEventsForDungeon(45, 2838, 62662)
    fetchAndSaveEventsForDungeon(45, 2839, 62662)

    fetchAndSaveEventsForDungeon(45, 3019, 62773)
    fetchAndSaveEventsForDungeon(45, 3020, 62773)
    fetchAndSaveEventsForDungeon(45, 3053, 62773)

    fetchAndSaveEventsForDungeon(45, 2424, 112441)
    fetchAndSaveEventsForDungeon(45, 2425, 112441)
    fetchAndSaveEventsForDungeon(45, 2437, 112441)
    fetchAndSaveEventsForDungeon(45, 2440, 112441)
    fetchAndSaveEventsForDungeon(45, 2441, 112441)

    fetchAndSaveEventsForDungeon(45, 2419, 112442)
    fetchAndSaveEventsForDungeon(45, 2426, 112442)
    fetchAndSaveEventsForDungeon(45, 2442, 112442)


def getSoazmiDf():
    return createEncounterDataFrame(
        45,
        2440,
        DifficultyType.Dungeon,
        112441,
        [],
        [PhaseAbilityTransition(1245634, "begincast", 0), PhaseAbilityTransition(1245634, "begincast", 1)],
    )


def getGrandMenagerieDf():
    return createEncounterDataFrame(
        45,
        2440,
        DifficultyType.Dungeon,
        112441,
        [],
        [PhaseAbilityTransition(181089, "cast", 1), PhaseAbilityTransition(181089, "cast", 2)],
    )


def getMyzasOasisDf():
    return createEncounterDataFrame(
        45, 2440, DifficultyType.Dungeon, 112441, [], [PhaseAbilityTransition(181089, "cast", 0)]
    )


def getHylbrandeDf():
    return createEncounterDataFrame(
        45,
        2426,
        DifficultyType.Dungeon,
        112442,
        [],
        [
            PhaseAbilityTransition(346766, "applybuff", 0),
            PhaseAbilityTransition(346766, "removebuff", 0),
            PhaseAbilityTransition(346766, "applybuff", 1),
            PhaseAbilityTransition(346766, "removebuff", 1),
        ],
    )


def getSoleahDf():
    return createEncounterDataFrame(
        45,
        2442,
        DifficultyType.Dungeon,
        112442,
        [],
        [
            PhaseAbilityTransition(181089, "cast", 0),
        ],
    )


def getAraKaraDf():
    return createEncounterDataFrame(
        45,
        2906,
        DifficultyType.Dungeon,
        62660,
        [],
        [
            PhaseAbilityTransition(434408, "removebuff", 0),
            PhaseAbilityTransition(434408, "removebuff", 1),
            PhaseAbilityTransition(434408, "removebuff", 2),
        ],
    )


def getForgeweaverArazDf():
    return createEncounterDataFrame(
        44,
        3132,
        DifficultyType.Mythic,
        0,
        [],
        [
            PhaseAbilityTransition(1230231, "cast", 0),
            PhaseAbilityTransition(1235338, "cast", 0),
            PhaseAbilityTransition(1230231, "cast", 1),
            PhaseAbilityTransition(1235338, "cast", 1),
        ],
    )


def getSoulHuntersDf():
    return createEncounterDataFrame(
        44,
        3122,
        DifficultyType.Mythic,
        0,
        [],
        [
            PhaseAbilityTransition(1233093, "applybuff", 0),
            PhaseAbilityTransition(1245978, "removebuff", 1),
            PhaseAbilityTransition(1233863, "applybuff", 0),
            PhaseAbilityTransition(1245978, "removebuff", 3),
            PhaseAbilityTransition(1233672, "cast", 0),
            PhaseAbilityTransition(1227117, "removebuff", 2),
        ],
    )


def getNexusKingSalhadaarDf():
    return createEncounterDataFrame(
        44,
        3134,
        DifficultyType.Mythic,
        0,
        [],
        [
            PhaseAbilityTransition(1227734, "cast", 0),  # Coalesce Voidwing
            PhaseAbilityTransition(1228065, "cast", 0),  # Rally the Shadowguard
            PhaseAbilityTransition(1228265, "applybuff", 0),  # King's Hunger
            PhaseAbilityTransition(1228265, "removebuff", 0),  # King's Hunger
        ],
    )


if __name__ == "__main__":
    printPhaseTimeStatistics(getSoazmiDf(), False, False, True)
