import json
import time
from src.fetchReports import (
    fetchAndSaveEvents,
    fetchAndSaveEventsForDungeon,
    fetchAndSaveFights,
    fetchAndSaveFightsForDungeon,
    fetchAndSaveReports,
    fetchFightsFromReport,
    fetchAndSaveFightsAsync,
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
    fetchAndSaveFightsAsync(44, 3129, DifficultyType.Heroic, KillType.Kills)
    fetchAndSaveFightsAsync(44, 3131, DifficultyType.Heroic, KillType.Kills)
    fetchAndSaveFightsAsync(44, 3130, DifficultyType.Heroic, KillType.Kills)
    fetchAndSaveFightsAsync(44, 3132, DifficultyType.Heroic, KillType.Kills)
    fetchAndSaveFightsAsync(44, 3122, DifficultyType.Heroic, KillType.Kills)
    fetchAndSaveFightsAsync(44, 3133, DifficultyType.Heroic, KillType.Kills)
    fetchAndSaveFightsAsync(44, 3134, DifficultyType.Heroic, KillType.Encounters)

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


def getZophexDf():
    return createEncounterDataFrame(
        45,
        2425,
        DifficultyType.Dungeon,
        112441,
        [],
        [
            PhaseAbilityTransition(346204, "cast", 0),
            PhaseAbilityTransition(346204, "cast", 1),
            PhaseAbilityTransition(346204, "cast", 2),
            PhaseAbilityTransition(346204, "cast", 3),
            PhaseAbilityTransition(346204, "cast", 4),
            PhaseAbilityTransition(346204, "cast", 5),
        ],
    )


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
        45,
        2440,
        DifficultyType.Dungeon,
        112441,
        [],
        [
            PhaseAbilityTransition(181089, "cast", 0),
            PhaseAbilityTransition(1241023, "removebuff", 0),
            PhaseAbilityTransition(1241023, "removebuff", 1),
        ],
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


def getPlexusSentinelDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        44,
        3129,
        difficultyType,
        0,
        [],
        [
            # Comment every other phase transition to get phase durations
            PhaseAbilityTransition(1220618, "applybuff", 0),
            PhaseAbilityTransition(1220618, "removebuff", 0),
            PhaseAbilityTransition(1220981, "applybuff", 0),
            PhaseAbilityTransition(1220981, "removebuff", 0),
            PhaseAbilityTransition(1220982, "applybuff", 0),
            PhaseAbilityTransition(1220982, "removebuff", 0),
        ],
    )


def getLoomitharDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        44,
        3131,
        difficultyType,
        0,
        [],
        [
            PhaseAbilityTransition(1228070, "applybuff", 0),
        ],
    )


def getSoulbinderNaazindhriDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(44, 3130, difficultyType)


def getForgeweaverArazDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        44,
        3132,
        difficultyType,
        0,
        [],
        [
            PhaseAbilityTransition(1230231, "cast", 0),
            PhaseAbilityTransition(1235338, "cast", 0),
            PhaseAbilityTransition(1230231, "cast", 1),
            PhaseAbilityTransition(1235338, "cast", 1),
        ],
    )


def getSoulHuntersDf(difficultyType: DifficultyType):
    if difficultyType == DifficultyType.Heroic:
        return createEncounterDataFrame(
            44,
            3122,
            difficultyType,
            0,
            [],
            [
                PhaseAbilityTransition(1242133, "applybuff", 1),
                PhaseAbilityTransition(1242133, "removebuff", 1),
                PhaseAbilityTransition(1242133, "applybuff", 3),
                PhaseAbilityTransition(1242133, "removebuff", 3),
                PhaseAbilityTransition(1242133, "applybuff", 5),
                PhaseAbilityTransition(1242133, "removebuff", 5),
            ],
            True,
        )
    else:
        return createEncounterDataFrame(
            44,
            3122,
            difficultyType,
            0,
            [],
            [
                PhaseAbilityTransition(1245978, "applybuff", 1),
                PhaseAbilityTransition(1245978, "removebuff", 1),
                PhaseAbilityTransition(1245978, "applybuff", 3),
                PhaseAbilityTransition(1245978, "removebuff", 3),
                PhaseAbilityTransition(1245978, "applybuff", 5),
                PhaseAbilityTransition(1245978, "removebuff", 5),
            ],
            True,
        )


def getFractillusDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(44, 3133, difficultyType)


def getNexusKingSalhadaarDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        44,
        3134,
        difficultyType,
        0,
        [],
        [
            PhaseAbilityTransition(1227734, "cast", 0),  # Coalesce Voidwing
            PhaseAbilityTransition(1228065, "cast", 0),  # Rally the Shadowguard
            PhaseAbilityTransition(1228265, "applybuff", 0),  # King's Hunger
            PhaseAbilityTransition(1228265, "removebuff", 0),  # King's Hunger
        ],
    )


def getDimDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        44,
        3135,
        difficultyType,
        0,
        [],
        [
            PhaseAbilityTransition(1234898, "cast", 0),  # Event Horizon
            PhaseAbilityTransition(1237689, "removebuff", 0),  # Void Shell
            PhaseAbilityTransition(1237689, "removebuff", 1),  # Void Shell
            PhaseAbilityTransition(1245292, "applydebuff", 0),  # Destabilized
        ],
        True,
        30,
    )


if __name__ == "__main__":
    # fetchAndSaveReports(44, 100, 20)
    # fetchAndSaveFights(44, 3122, DifficultyType.Heroic, KillType.Kills, True, 200)
    # fetchAndSaveEvents(44, 3122, DifficultyType.Heroic, True)
    printPhaseTimeStatistics(getSoulHuntersDf(DifficultyType.Heroic), False, False, True)
