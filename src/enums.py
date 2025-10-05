from enum import StrEnum, IntEnum


class KillType(StrEnum):
    Encounters = "Encounters"
    Kills = "Kills"


class DifficultyType(IntEnum):
    Dungeon = 0
    Normal = 3
    Heroic = 4
    Mythic = 5
