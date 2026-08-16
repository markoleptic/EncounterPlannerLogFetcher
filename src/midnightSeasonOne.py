from src.enums import DifficultyType, KillType
from src.fetchReports import (
    fetchAndSaveEvents,
    fetchAndSaveEventsForDungeon,
    fetchAndSaveFights,
    fetchAndSaveFightsForDungeon,
)
from src.processEvents import PhaseAbilityTransition, createEncounterDataFrame


def fetchAndSaveFightsAndEventsMythic():
    # fetchAndSaveFights(46, 3176, DifficultyType.Mythic, KillType.Kills, False, 100)  # Averzian
    fetchAndSaveFights(46, 3177, DifficultyType.Mythic, KillType.Kills, False, 100)  # Vorasius
    fetchAndSaveFights(46, 3178, DifficultyType.Mythic, KillType.Kills, False, 100)  # Vaelgor & Ezzorak
    fetchAndSaveFights(46, 3179, DifficultyType.Mythic, KillType.Kills, False, 100)  # Fallen-King Salhadaar
    # fetchAndSaveFights(46, 3180, DifficultyType.Mythic, KillType.Kills, False, 200) # Lightblinded Vanguard
    # fetchAndSaveFights(46, 3181, DifficultyType.Mythic, KillType.Kills, False, 200) # Crown

    fetchAndSaveFights(46, 3306, DifficultyType.Mythic, KillType.Kills, False, 100)  # Chimaerus

    # fetchAndSaveFights(46, 3182, DifficultyType.Mythic, KillType.Kills, False, 200)  # Belo'ren
    # fetchAndSaveFights(46, 3183, DifficultyType.Mythic, KillType.Kills, False, 200)  # Midnight Falls

    fetchAndSaveEvents(46, 3176, DifficultyType.Mythic)  # Averzian
    fetchAndSaveEvents(46, 3177, DifficultyType.Mythic)  # Vorasius
    fetchAndSaveEvents(46, 3178, DifficultyType.Mythic)  # Vaelgor & Ezzorak
    fetchAndSaveEvents(46, 3179, DifficultyType.Mythic)  # Fallen-King Salhadaar
    # fetchAndSaveEvents(46, 3180, DifficultyType.Mythic)  # Lightblinded Vanguard
    # fetchAndSaveEvents(46, 3181, DifficultyType.Mythic) # Crown

    fetchAndSaveEvents(46, 3306, DifficultyType.Mythic)  # Chimaerus

    # fetchAndSaveEvents(46, 3182, DifficultyType.Mythic)  # Belo'ren
    # fetchAndSaveEvents(46, 3183, DifficultyType.Mythic)  # Midnight Falls


def fetchAndSaveFightsAndEventsHeroic(override: bool = True):
    fetchAndSaveFights(46, 3176, DifficultyType.Heroic, KillType.Kills, override, 100)  # Averzian
    fetchAndSaveFights(46, 3177, DifficultyType.Heroic, KillType.Kills, override, 100)  # Vorasius
    fetchAndSaveFights(46, 3178, DifficultyType.Heroic, KillType.Kills, override, 100)  # Vaelgor & Ezzorak
    fetchAndSaveFights(46, 3179, DifficultyType.Heroic, KillType.Kills, override, 100)  # Fallen-King Salhadaar
    fetchAndSaveFights(46, 3180, DifficultyType.Heroic, KillType.Kills, override, 100)  # Lightblinded Vanguard
    fetchAndSaveFights(46, 3181, DifficultyType.Heroic, KillType.Kills, override, 100)  # Crown
    fetchAndSaveFights(46, 3306, DifficultyType.Heroic, KillType.Kills, override, 100)  # Chimaerus
    fetchAndSaveFights(46, 3182, DifficultyType.Heroic, KillType.Kills, override, 100)  # Belo'ren
    fetchAndSaveFights(46, 3183, DifficultyType.Heroic, KillType.Kills, override, 100)  # Midnight Falls

    fetchAndSaveEvents(46, 3176, DifficultyType.Heroic, override)  # Averzian
    fetchAndSaveEvents(46, 3177, DifficultyType.Heroic, override)  # Vorasius
    fetchAndSaveEvents(46, 3178, DifficultyType.Heroic, override)  # Vaelgor & Ezzorak
    fetchAndSaveEvents(46, 3179, DifficultyType.Heroic, override)  # Fallen-King Salhadaar
    fetchAndSaveEvents(46, 3180, DifficultyType.Heroic, override)  # Lightblinded Vanguard
    fetchAndSaveEvents(46, 3181, DifficultyType.Heroic, override)  # Crown
    fetchAndSaveEvents(46, 3306, DifficultyType.Heroic, override)  # Chimaerus
    fetchAndSaveEvents(46, 3182, DifficultyType.Heroic, override)  # Belo'ren
    fetchAndSaveEvents(46, 3183, DifficultyType.Heroic, override)  # Midnight Falls


def fetchAndSaveFightsAndEventsDungeons(override: bool = True):
    fetchAndSaveFightsForDungeon(47, 112526, override, 100)  # Alg
    fetchAndSaveFightsForDungeon(47, 12811, override, 100)  # Magisters
    fetchAndSaveFightsForDungeon(47, 12874, override, 100)  # Maisara
    fetchAndSaveFightsForDungeon(47, 12915, override, 100)  # Nexus-Point
    fetchAndSaveFightsForDungeon(47, 10658, override, 100)  # Pit
    fetchAndSaveFightsForDungeon(47, 361753, override, 100)  # Seat
    fetchAndSaveFightsForDungeon(47, 61209, override, 100)  # Skyreach
    fetchAndSaveFightsForDungeon(47, 12805, override, 100)  # Windrunner

    fetchAndSaveEventsForDungeon(47, 2562, 112526, override)  # Alg
    fetchAndSaveEventsForDungeon(47, 2563, 112526, override)  # Alg
    fetchAndSaveEventsForDungeon(47, 2564, 112526, override)  # Alg
    fetchAndSaveEventsForDungeon(47, 2565, 112526, override)  # Alg

    fetchAndSaveEventsForDungeon(47, 3071, 12811, override)  # Magisters
    fetchAndSaveEventsForDungeon(47, 3072, 12811, override)  # Magisters
    fetchAndSaveEventsForDungeon(47, 3073, 12811, override)  # Magisters
    fetchAndSaveEventsForDungeon(47, 3074, 12811, override)  # Magisters

    fetchAndSaveEventsForDungeon(47, 3212, 12874, override)  # Maisara
    fetchAndSaveEventsForDungeon(47, 3213, 12874, override)  # Maisara
    fetchAndSaveEventsForDungeon(47, 3214, 12874, override)  # Maisara

    fetchAndSaveEventsForDungeon(47, 3328, 12915, override)  # Nexus-Point
    fetchAndSaveEventsForDungeon(47, 3332, 12915, override)  # Nexus-Point
    fetchAndSaveEventsForDungeon(47, 3333, 12915, override)  # Nexus-Point

    fetchAndSaveEventsForDungeon(47, 1999, 10658, override)  # Pit
    fetchAndSaveEventsForDungeon(47, 2001, 10658, override)  # Pit
    fetchAndSaveEventsForDungeon(47, 2000, 10658, override)  # Pit

    fetchAndSaveEventsForDungeon(47, 2065, 361753, override)  # Seat
    fetchAndSaveEventsForDungeon(47, 2066, 361753, override)  # Seat
    fetchAndSaveEventsForDungeon(47, 2067, 361753, override)  # Seat
    fetchAndSaveEventsForDungeon(47, 2068, 361753, override)  # Seat

    fetchAndSaveEventsForDungeon(47, 1698, 61209, override)  # Skyreach
    fetchAndSaveEventsForDungeon(47, 1699, 61209, override)  # Skyreach
    fetchAndSaveEventsForDungeon(47, 1700, 61209, override)  # Skyreach
    fetchAndSaveEventsForDungeon(47, 1701, 61209, override)  # Skyreach

    fetchAndSaveEventsForDungeon(47, 3056, 12805, override)  # Windrunner
    fetchAndSaveEventsForDungeon(47, 3057, 12805, override)  # Windrunner
    fetchAndSaveEventsForDungeon(47, 3058, 12805, override)  # Windrunner
    fetchAndSaveEventsForDungeon(47, 3059, 12805, override)  # Windrunner


def getAverzianDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(zoneID=46, encounterID=3176, difficulty=difficultyType)


def getVorasiusDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(zoneID=46, encounterID=3177, difficulty=difficultyType)


def getVaelgorAndEzzorakDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        zoneID=46,
        encounterID=3178,
        difficulty=difficultyType,
        # phaseAbilities=[
        #     PhaseAbilityTransition(1249748, "removebuff", 0),
        #     PhaseAbilityTransition(1249748, "removebuff", 2),
        #     PhaseAbilityTransition(1249748, "removebuff", 4),
        # ],
    )


def getFallenKingSalhadaarDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        zoneID=46,
        encounterID=3179,
        difficulty=difficultyType,
        phaseAbilities=[
            PhaseAbilityTransition(1246175, "cast", 0),
            PhaseAbilityTransition(1271577, "cast", 0),
            PhaseAbilityTransition(1246175, "cast", 1),
            PhaseAbilityTransition(1271577, "cast", 1),
            PhaseAbilityTransition(1246175, "cast", 2),
            PhaseAbilityTransition(1271577, "cast", 2),
        ],
    )


def getLightblindedVanguardDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(zoneID=46, encounterID=3180, difficulty=difficultyType)


def getChimaerusDf(difficultyType: DifficultyType):
    return createEncounterDataFrame(
        zoneID=46,
        encounterID=3306,
        difficulty=difficultyType,
        phaseAbilities=[
            PhaseAbilityTransition(1252863, "removebuff", 0),
            PhaseAbilityTransition(1252863, "applybuff", 1),
            PhaseAbilityTransition(1252863, "removebuff", 1),
            PhaseAbilityTransition(1252863, "applybuff", 2),
            PhaseAbilityTransition(1252863, "removebuff", 2),
            PhaseAbilityTransition(1252863, "applybuff", 3),
            PhaseAbilityTransition(1252863, "removebuff", 3),
            PhaseAbilityTransition(1252863, "applybuff", 4),
        ],
    )


def getCrawthDf():
    return createEncounterDataFrame(
        zoneID=49,
        encounterID=2564,
        difficulty=DifficultyType.Dungeon,
        dungeonEncounterID=112526,
        phaseAbilities=[
            PhaseAbilityTransition(181089, "cast", 0),
            PhaseAbilityTransition(181089, "cast", 2),
        ],
    )
