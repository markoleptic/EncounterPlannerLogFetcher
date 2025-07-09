import json
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from src.enums import DifficultyType, KillType
from typing import Any, Dict

from src.utility import getAccessToken, getEventsPath, getFightsPath, getReportsPath


def fetchReports(accessToken: str, page: int, zoneID: int, reportLimit: int = 0) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query (
        $page: Int!,
        $zoneID: Int!
        $reportLimit: Int
    ) {
        reportData {
            reports(page: $page, zoneID: $zoneID, limit: $reportLimit) {
                current_page
                data {
                    code
                }
                has_more_pages
            }
        }
    }"""

    variables = {
        "page": page,
        "zoneID": zoneID,
        "reportLimit": reportLimit,
    }

    return client.execute(gql(query), variables)


def fetchAndSaveReports(zoneID: int, reportLimit: int = 100, maxPages: int = 10):
    token = getAccessToken()
    page = 1
    reportCodes = []

    while page <= maxPages:
        try:
            print(f"Fetching page {page}...")
            result = fetchReports(token, page, zoneID, reportLimit)

            reportsData = result["reportData"]["reports"]["data"]
            print(f"Found {len(reportsData)} reports on page {page}")

            for report in reportsData:
                code = report["code"]
                reportCodes.append(code)

            if not result["reportData"]["reports"]["has_more_pages"]:
                print("No more pages.")
                break

            page += 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    path = getReportsPath() / f"{zoneID}.json"
    with open(path, "w") as reportFile:
        json.dump(
            {"zoneID": zoneID, "lastPage": page, "codes": reportCodes},
            reportFile,
            indent=2,
        )


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
    reportLimit: int,
    maxPages: int,
):
    token = getAccessToken()
    results = []

    with open(getReportsPath() / f"{zoneID}.json") as reportsFile:
        reports = json.load(reportsFile)
        codes = reports["codes"]
        for code in codes:
            try:
                print(f"Fetching fights for {code}...")
                result = fetchFightsFromReport(token, code, encounterID, difficulty, killType)

                fightsData = result["reportData"]["report"]["fights"]
                print(f"Found {len(fightsData)} fights for {code}")

                for fight in fightsData:
                    fightID = fight["id"]
                    startTime = fight["startTime"]

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

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                continue

    with open(getFightsPath() / f"{zoneID}_{encounterID}_{difficulty}.json", "w") as fight_id_file:
        json.dump(
            results,
            fight_id_file,
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

    variables = {
        "code": code,
        "fightIDs": fightIDs,
        "startTime": startTime,
    }

    return client.execute(gql(query), variables)


def fetchAndSaveEvents(zoneID: int, encounterID: int, difficulty: DifficultyType):
    token = getAccessToken()

    with open(getFightsPath() / f"{zoneID}_{encounterID}_{difficulty}.json") as fightsFile:
        fightObjects = json.load(fightsFile)

        for fightObject in fightObjects:
            code = fightObject["code"]
            fightID = fightObject["id"]
            fightStartTime = fightObject["startTime"]
            startTime = 0.0
            eventsData = []
            try:
                print(f"Fetching events for {code}, {fightID}...")

                while True:
                    result = fetchEvents(token, code, [fightID], startTime)
                    currentEventsData = result["reportData"]["report"]["events"]["data"]
                    count = len(currentEventsData)
                    print(f"Found {count} events for {code}, {fightID}")

                    if count > 0:
                        eventsData.extend(currentEventsData)

                    nextPageTimestamp = result["reportData"]["report"]["events"]["nextPageTimestamp"]
                    if nextPageTimestamp:
                        startTime = nextPageTimestamp
                    else:
                        break

                if len(eventsData) > 0:
                    path = getEventsPath() / f"{zoneID}_{encounterID}_{difficulty}_{code}_{fightID}.json"
                    with open(path, "w") as eventsFile:
                        json.dump(
                            {
                                "startTime": fightStartTime,
                                "events": eventsData,
                            },
                            eventsFile,
                            indent=2,
                        )

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                continue


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
