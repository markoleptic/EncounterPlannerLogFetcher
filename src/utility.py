from dotenv import load_dotenv
import json
import os
import requests
import time
from pathlib import Path

from src.enums import DifficultyType

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def createDirectoriesIfNecessary():
    if not os.path.isdir(getReportsPath()):
        os.mkdir(getReportsPath())
    if not os.path.isdir(getFightsPath()):
        os.mkdir(getFightsPath())
    if not os.path.isdir(getTempPath()):
        os.mkdir(getTempPath())
    if not os.path.isdir(PROJECT_ROOT / "events"):
        os.mkdir(PROJECT_ROOT / "events")


def getProjectRoot() -> Path:
    return PROJECT_ROOT


def getEventsPath(zoneID: int, difficulty: DifficultyType, encounterID: int) -> Path:
    return PROJECT_ROOT / "events" / str(zoneID) / str(difficulty) / str(encounterID)


def getEventsFilePath(zoneID: int, difficulty: DifficultyType, encounterID: int, code: str, fightID: int) -> Path:
    zoneIdDirectory = PROJECT_ROOT / "events" / str(zoneID)
    if not os.path.isdir(zoneIdDirectory):
        os.mkdir(zoneIdDirectory)
    difficultyDirectory = zoneIdDirectory / str(difficulty)
    if not os.path.isdir(difficultyDirectory):
        os.mkdir(difficultyDirectory)
    encounterIdDirectory = difficultyDirectory / str(encounterID)
    if not os.path.isdir(encounterIdDirectory):
        os.mkdir(encounterIdDirectory)
    return getEventsPath(zoneID, difficulty, encounterID) / f"{zoneID}_{encounterID}_{difficulty}_{code}_{fightID}.json"


def getEventsFilePathForDungeon(
    zoneID: int, dungeonEncounterID: int, encounterID: int, code: str, fightID: int, pullID: int
) -> Path:
    return (
        getEventsPath(zoneID, DifficultyType.Dungeon, dungeonEncounterID)
        / str(encounterID)
        / f"{zoneID}_{encounterID}_{DifficultyType.Dungeon}_{code}_{fightID}_{pullID}.json"
    )


def getReportsPath() -> Path:
    return PROJECT_ROOT / "reports"


def getReportsFilePath(zoneID: int) -> Path:
    return getReportsPath() / f"{zoneID}.json"


def getFightsPath() -> Path:
    return PROJECT_ROOT / "fights"


def getFightsFilePath(zoneID: int, difficulty: DifficultyType, encounterID: int) -> Path:
    return getFightsPath() / f"{zoneID}_{encounterID}_{difficulty}.json"


def getTempPath() -> Path:
    return PROJECT_ROOT / "temp"


def getAccessToken() -> str:
    tokenPath = getProjectRoot() / "token.json"
    token = None
    if os.path.exists(tokenPath):
        with open(tokenPath) as tokenFile:
            jsonToken = json.load(tokenFile)
            if jsonToken["expires_at"] > time.time():
                token = jsonToken["access_token"]

    if token == None:
        url = "https://www.warcraftlogs.com/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        jsonResponse = response.json()
        token = jsonResponse["access_token"]
        jsonToken = {
            "access_token": token,
            "expires_at": int(time.time()) + jsonResponse["expires_in"] - 60,
        }
        with open(tokenPath, "w") as tokenFile:
            json.dump(jsonToken, tokenFile)

    return token
