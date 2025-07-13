import json
from pathlib import Path
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from src.enums import DifficultyType, KillType
from typing import Any, Dict, List, Set

from src.utility import getAccessToken, getEventsFilePath, getFightsFilePath, getReportsFilePath


def fetchReports(
    accessToken: str, page: int, zoneID: int, reportLimit: int = 0, startTime: float = 0.0
) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query (
        $page: Int!
        $zoneID: Int!
        $reportLimit: Int
        $startTime: Float
    ) {
        reportData {
            reports(page: $page, zoneID: $zoneID, limit: $reportLimit, startTime: $startTime) {
                current_page
                data {
                    code
                    startTime
				    endTime
                }
                has_more_pages
            }
        }
    }"""

    variables = {"page": page, "zoneID": zoneID, "reportLimit": reportLimit, "startTime": startTime}

    return client.execute(gql(query), variables)


def fetchAndSaveReports(
    zoneID: int,
    reportLimit: int = 100,
    maxPages: int = 10,
    startTime: float = -1.0,
    reportsFilePath: Path | None = None,
):
    token = getAccessToken()
    page = 1
    reportCodes = []

    if reportsFilePath == None:
        reportsFilePath = getReportsFilePath(zoneID)
    if reportsFilePath.exists():
        with open(reportsFilePath) as reportsFile:
            lastData = json.load(reportsFile)
            reportCodes = lastData["codes"]
            print(f"Loaded: {len(reportCodes)} codes from {reportsFilePath}")
            if startTime == -1.0:
                startTime = lastData.get("startTime", 0.0)
                print(f"Using last saved start time: {startTime}")

    maxStartTime = startTime

    while page <= maxPages:
        try:
            print(f"Fetching page {page}...")
            result = fetchReports(token, page, zoneID, reportLimit, startTime)

            reportData = result["reportData"]
            reports = reportData["reports"]["data"]

            print(f"Found {len(reports)} reports on page {page}")
            for report in reports:
                maxStartTime = max(maxStartTime, report["startTime"])
                code = report["code"]
                if not code in reportCodes:
                    reportCodes.append(report["code"])

            if not result["reportData"]["reports"]["has_more_pages"]:
                print("No more pages.")
                break

            page += 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    with open(reportsFilePath, "w") as reportsFile:
        json.dump(
            {"zoneID": zoneID, "lastPage": page, "codes": reportCodes, "startTime": maxStartTime},
            reportsFile,
            indent=2,
        )


def fetchFightFromReport(accessToken: str, code: str, fightID: int) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query ($code: String, $fightIDs: [Int]) {
        reportData {
            report(code: $code) {
                fights(fightIDs: $fightIDs) {
                    id
                    startTime
                }
            }
        }
    }"""

    variables = {
        "code": code,
        "fightIDs": [fightID],
    }

    return client.execute(gql(query), variables)


def fetchFightsFromReport(
    accessToken: str, code: str, encounterID: int, difficulty: DifficultyType, killType: KillType
) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query (
        $code: String
        $difficulty: Int
        $encounterID: Int
        $killType: KillType
    ) {
        reportData {
            report(code: $code) {
                fights(
                    difficulty: $difficulty
                    encounterID: $encounterID
                    killType: $killType
                ) {
                    id
                    startTime
                    fightPercentage
                    keystoneLevel
					keystoneTime
					phaseTransitions {
						id
						startTime
					}
                }
            }
        }
    }"""

    variables = {
        "code": code,
        "encounterID": encounterID,
        "difficulty": difficulty,
        "killType": killType,
    }

    return client.execute(gql(query), variables)


def fetchAndSaveFights(
    zoneID: int,
    encounterID: int,
    difficulty: DifficultyType,
    killType: KillType,
    overwriteExisting: bool = False,
    foundFightLimit: int = 0,
    reportsFilePath: Path | None = None,
):
    if reportsFilePath == None:
        reportsFilePath = getReportsFilePath(zoneID)
    if not reportsFilePath.exists():
        print(f"No reports file for zoneID: {zoneID}")
        return

    with open(reportsFilePath) as reportsFile:
        reports = json.load(reportsFile)
        codes: List[str] = reports["codes"]

    fightsFilePath = getFightsFilePath(zoneID, difficulty, encounterID)
    results: List[Dict[str, Any]] = []

    if not overwriteExisting and fightsFilePath.exists():
        with open(fightsFilePath) as fightsFile:
            results = json.load(fightsFile)

    seenCodes: Set[str] = {r["code"] for r in results}

    count = 0
    token = getAccessToken()
    for code in codes:
        if code in seenCodes:
            continue

        print(f"Fetching fights for code: {code}...")
        try:
            result = fetchFightsFromReport(token, code, encounterID, difficulty, killType)
        except Exception as e:
            print(f"Error fetching report {code!r}: {e}")
            break

        fightsData = result["reportData"]["report"]["fights"]
        print(f"Found {len(fightsData)} fights")

        if len(fightsData) == 0:
            results.append({"code": code})
        else:
            for fight in fightsData:
                fightID = fight.get("id")
                startTime = fight.get("startTime")
                if fightID and startTime:
                    results.append(
                        {
                            "code": code,
                            "id": fightID,
                            "startTime": startTime,
                            "fightPercentage": fight["fightPercentage"],
                            "keystoneLevel": fight["keystoneLevel"] or None,
                            "phaseTransitions": fight["phaseTransitions"] or None,
                        }
                    )
                    count += 1
        seenCodes.add(code)

        if foundFightLimit > 0 and count >= foundFightLimit:
            print(f"Hit found fight limit of {foundFightLimit}, stopping")
            break

    with open(fightsFilePath, "w") as fightsFile:
        json.dump(results, fightsFile, indent=2)


def fetchEvents(accessToken: str, code: str, fightIDs: list[int], startTime: float) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query($code: String, $fightIDs: [Int], $startTime: Float) {
        reportData {
            report(code: $code) {
                events(
                    fightIDs: $fightIDs
                    dataType: Casts
                    hostilityType: Enemies
                    limit: 10000
                    startTime: $startTime
                    wipeCutoff: 0
                ) {
                    data
                    nextPageTimestamp
                }
            }
        }
    }"""

    variables = {"code": code, "fightIDs": fightIDs, "startTime": startTime}

    return client.execute(gql(query), variables)


def fetchAndSaveEvents(zoneID: int, encounterID: int, difficulty: DifficultyType, overwriteExisting: bool = False):
    fightsFilePath = getFightsFilePath(zoneID, difficulty, encounterID)
    if not fightsFilePath.exists():
        print(f"No fights file for zoneID:{zoneID}, encounterID:{encounterID}, difficulty:{difficulty}")
        return

    fightObjects = {}
    with open(fightsFilePath) as fightsFile:
        fightObjects = json.load(fightsFile)

    token = getAccessToken()

    for fightObject in fightObjects:
        code = fightObject.get("code")
        fightID = fightObject.get("id")
        if not fightID:
            continue

        fightStartTime = fightObject["startTime"]
        startTime = 0.0
        eventsData = []

        eventsFilePath = getEventsFilePath(zoneID, difficulty, encounterID, code, fightID)
        if not eventsFilePath.exists() or overwriteExisting:
            try:
                print(f"Fetching events for code: {code}, fightID: {fightID}...")
                while startTime != None:
                    result = fetchEvents(token, code, [fightID], startTime)
                    currentEventsData = result["reportData"]["report"]["events"]["data"]
                    count = len(currentEventsData)
                    print(f"Found {count} events")
                    if count > 0:
                        eventsData.extend(currentEventsData)
                    startTime = result["reportData"]["report"]["events"]["nextPageTimestamp"]

            except Exception as e:
                print(f"Error fetching events for: {code}, fightID: {fightID}: {e}")
                return

        if len(eventsData) > 0:
            with open(eventsFilePath, "w") as eventsFile:
                json.dump({"startTime": fightStartTime, "events": eventsData}, eventsFile, indent=2)


def fetchReportsComplex(
    accessToken: str,
    page: int,
    zoneID: int,
    encounterID: int,
    difficulty: DifficultyType,
    killType: KillType,
    reportLimit: int = 0,
) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query (
        $page: Int!,
        $zoneID: Int!
        $encounterID: Int!
        $difficulty: Int!
        $killType: KillType!
        $reportLimit: Int
    ) {
        reportData {
            reports(zoneID: $zoneID, page: $page, limit: $reportLimit) {
                current_page
                data {
                    code
                    startTime
                    endTime
                    fights(
                        encounterID: $encounterID
                        difficulty: $difficulty
                        killType: $killType
                    ) {
                        id
                        encounterID
                        name
                        startTime
                        endTime
                        kill
                        fightPercentage
                        keystoneLevel
                        keystoneTime
                        phaseTransitions {
                            id
                            startTime
                        }
                    }
                }
                from
                to
                per_page
                total
            }
        }
    }"""

    variables = {
        "page": page,
        "zoneID": zoneID,
        "encounterID": encounterID,
        "difficulty": difficulty,
        "killType": killType,
        "reportLimit": reportLimit,
    }

    return client.execute(gql(query), variables)
