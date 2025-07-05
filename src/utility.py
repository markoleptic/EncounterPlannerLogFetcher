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


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_events_path() -> Path:
    return PROJECT_ROOT / "events"


def get_reports_path() -> Path:
    return PROJECT_ROOT / "reports"


def get_fights_path() -> Path:
    return PROJECT_ROOT / "fights"


def get_access_token() -> str:
    token_path = get_project_root() / "token.json"
    token = None
    if os.path.exists(token_path):
        with open(token_path) as token_file:
            json_token = json.load(token_file)
            if json_token["expires_at"] > time.time():
                token = json_token["access_token"]

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
        json_response = response.json()
        token = json_response["access_token"]
        json_token = {
            "access_token": token,
            "expires_at": int(time.time()) + json_response["expires_in"] - 60,
        }
        with open(token_path, "w") as f:
            json.dump(json_token, f)

    return token
