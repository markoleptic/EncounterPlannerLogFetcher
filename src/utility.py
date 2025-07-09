from dotenv import load_dotenv
import json
import os
import requests
import time
from pathlib import Path

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def getProjectRoot() -> Path:
    return PROJECT_ROOT


def getEventsPath() -> Path:
    return PROJECT_ROOT / "events"


def getReportsPath() -> Path:
    return PROJECT_ROOT / "reports"


def getFightsPath() -> Path:
    return PROJECT_ROOT / "fights"


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
