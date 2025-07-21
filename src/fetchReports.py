import json
import time
from pathlib import Path
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportServerError
from src.enums import DifficultyType, KillType
from typing import Any, Callable, Dict, List, Set
from functools import partial

from src.utility import (
    getAccessToken,
    getEventsFilePath,
    getEventsFilePathForDungeon,
    getFightsFilePath,
    getReportsFilePath,
)

rateLimitQuery = """
query {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
        pointsResetIn
    } 
}
"""

fetchReportsQuery = """
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

fetchFightFromReportQuery = """
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

fetchFightsFromReportsQuery = """
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
                phaseTransitions {
                    id
                    startTime
                }
            }
        }
    }
}"""

fetchDungeonFightsFromReportQuery = """
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
                dungeonPulls {
                    encounterID
                    startTime
                    endTime
                }
            }
        }
    }
}"""

fetchEventsQuery = """
query(
    $code: String
    $fightIDs: [Int]
    $startTime: Float
    $endTime: Float
    $filterExpression: String
    $dataType: EventDataType
) {
    reportData {
        report(code: $code) {
            events(
                fightIDs: $fightIDs
                filterExpression: $filterExpression
                dataType: $dataType
                limit: 10000
                startTime: $startTime
                endTime: $endTime
                wipeCutoff: 0
            ) {
                data
                nextPageTimestamp
            }
        }
    }
}"""

nextPointsResetTime = 0


def updatePointsResetTime(accessToken: str):
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    rateLimitResponse = client.execute(gql(rateLimitQuery))
    rateLimitData = rateLimitResponse.get("rateLimitData")
    secondsUntilPointsReset = 3600
    if rateLimitData:
        secondsUntilPointsReset = rateLimitData.get("pointsResetIn")
    nextPointsResetTime = time.time() + secondsUntilPointsReset
    print(f"Updated next points reset time: {nextPointsResetTime}")


updatePointsResetTime(getAccessToken())


def sleepUntilPointsReset(
    transportServerError: TransportServerError, accessToken: str, callback: Callable[[], Any]
) -> Any:
    if transportServerError.code == 429:
        time.sleep(nextPointsResetTime)
        updatePointsResetTime(accessToken)
        return callback()
    return None


def executeQueryWithRetry(accessToken: str, query: str, variables: Dict[str, Any]) -> Any:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    try:
        return client.execute(gql(query), variables)
    except TransportServerError as e:
        if not sleepUntilPointsReset(e, accessToken, partial(executeQueryWithRetry, accessToken, query, variables)):
            raise


def fetchReports(
    accessToken: str, page: int, zoneID: int, reportLimit: int = 0, startTime: float = 0.0
) -> Dict[str, Any]:
    """Fetches a page of reports.

    Args:
        accessToken (str): WarcraftLogs API access token.
        page (int): Current page for the query.
        zoneID (int): WarcraftLogs API zone ID for the raid or dungeon.
        reportLimit (int, optional): Upper limit on the number of reports per page. Defaults to 0.
        startTime (float, optional): Reports will be filtered to have occurred after this time. Defaults to 0.0.

    Returns:
        Dict[str, Any]: Found reports.
    """

    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    variables = {"page": page, "zoneID": zoneID, "reportLimit": reportLimit, "startTime": startTime}

    return executeQueryWithRetry(accessToken, fetchReportsQuery, variables)


def fetchAndSaveReports(
    zoneID: int,
    reportLimit: int = 100,
    maxPages: int = 10,
    startTime: float = -1.0,
    reportsFilePath: Path | None = None,
):
    """Fetches reports codes and saves them to file. If a matching reports file exists, it will be loaded so that
    duplicate codes are not recorded. If startTime is not specified and a matching reports file exists, it will use the
    saved start time to limit the fetched reports to have occurred after this time.

    Args:
        zoneID (int): WarcraftLogs API zone ID for the raid or dungeon.
        reportLimit (int, optional): Upper limit on the number of reports per page. Defaults to 100.
        maxPages (int, optional): Upper limit on the number of total pages. Defaults to 10.
        startTime (float, optional): Reports will be filtered to have occurred after this time. Defaults to -1.0.
        reportsFilePath (Path | None, optional): If specified, uses this file for report codes, otherwise defaulting to
            the default report file path for the zoneID. Defaults to None.
    """

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
            break

    with open(reportsFilePath, "w") as reportsFile:
        json.dump(
            {"zoneID": zoneID, "lastPage": page, "codes": reportCodes, "startTime": maxStartTime},
            reportsFile,
            indent=2,
        )


def fetchFightFromReport(accessToken: str, code: str, fightID: int) -> Dict[str, Any]:
    """Obtains a single fight from a report.

    Args:
        accessToken (str): WarcraftLogs API access token.
        code (str): Report code.
        fightID (int): Fight ID in the report.

    Returns:
        Dict[str, Any]: Found fight.
    """

    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    variables = {
        "code": code,
        "fightIDs": [fightID],
    }

    return executeQueryWithRetry(accessToken, fetchFightFromReportQuery, variables)


def fetchFightsFromReport(
    accessToken: str, code: str, encounterID: int, difficulty: DifficultyType, killType: KillType
) -> Dict[str, Any]:
    """Fetches fights from a report for a given raid.

    Args:
        accessToken (str): WarcraftLogs API access token.
        code (str): Report code.
        encounterID (int): Encounter ID for the boss (Translates to dungeonEncounterID in game).
        difficulty (DifficultyType): Difficulty type to filter fights by.
        killType (KillType): Kill type to filter fights by.

    Returns:
        Dict[str, Any]: Found fights.
    """

    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    variables = {
        "code": code,
        "encounterID": encounterID,
        "difficulty": difficulty,
        "killType": killType,
    }

    return executeQueryWithRetry(accessToken, fetchFightsFromReportsQuery, variables)


def fetchDungeonFightsFromReport(accessToken: str, code: str, dungeonEncounterID: int) -> Dict[str, Any]:
    """Fetches fights from a report for a given dungeon. Each fight entry includes dungeon pulls that are tagged with
    the actual encounter ID, relative start time, and relative end time.

    Args:
        accessToken (str): WarcraftLogs API access token.
        code (str): Report code.
        dungeonEncounterID (int): The WarcraftLogs dungeon encounter ID (doesn't translate to anything in game?)

    Returns:
        Dict[str, Any]: Found fights.
    """

    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    variables = {
        "code": code,
        "encounterID": dungeonEncounterID,
        "difficulty": DifficultyType.Dungeon,
        "killType": KillType.Kills,
    }

    return executeQueryWithRetry(accessToken, fetchDungeonFightsFromReportQuery, variables)


def fetchAndSaveFights(
    zoneID: int,
    encounterID: int,
    difficulty: DifficultyType,
    killType: KillType,
    overwriteExisting: bool = False,
    foundFightLimit: int = 0,
    reportsFilePath: Path | None = None,
):
    """Fetches fights for raid encounters from a list of report IDs and saves the fight IDs to the fights directory as
    a single file.

    Args:
        zoneID (int): WarcraftLogs API zone ID for the raid.
        encounterID (int): Encounter ID for the boss (Translates to dungeonEncounterID in game).
        difficulty (DifficultyType): Difficulty type to filter fights by.
        killType (KillType): Kill type to filter fights by.
        overwriteExisting (bool, optional): Whether to overwrite the fights file. Defaults to False.
        foundFightLimit (int, optional): Upper limit on the number of fights to fetch. Defaults to 0.
        reportsFilePath (Path | None, optional): If specified, uses this file for report codes, otherwise defaulting to
            the default report file path for the zoneID. Defaults to None.
    """

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
            continue

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


def fetchAndSaveFightsForDungeon(
    zoneID: int,
    dungeonEncounterID: int,
    overwriteExisting: bool = False,
    foundFightLimit: int = 0,
    reportsFilePath: Path | None = None,
):
    """Fetches fights for dungeon encounters from a list of report IDs and saves the fights to the fights directory
    as a single file. Each fight entry includes dungeon pulls that are tagged with the actual encounter ID, relative
    start time, and relative end time.

    Args:
        zoneID (int): WarcraftLogs API zone ID for the dungeon.
        dungeonEncounterID (int): The WarcraftLogs dungeon encounter ID (doesn't translate to anything in game?)
        overwriteExisting (bool, optional): Whether to overwrite the fights file. Defaults to False. Defaults to False.
        foundFightLimit (int, optional): Upper limit on the number of fights to fetch. Defaults to 0.
        reportsFilePath (Path | None, optional): If specified, uses this file for report codes, otherwise defaulting to
            the default report file path for the zoneID. Defaults to None.
    """

    if reportsFilePath == None:
        reportsFilePath = getReportsFilePath(zoneID)
    if not reportsFilePath.exists():
        print(f"No reports file for zoneID: {zoneID}")
        return

    with open(reportsFilePath) as reportsFile:
        reports = json.load(reportsFile)
        codes: List[str] = reports["codes"]

    fightsFilePath = getFightsFilePath(zoneID, DifficultyType.Dungeon, dungeonEncounterID)
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
            result = fetchDungeonFightsFromReport(token, code, dungeonEncounterID)
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
                            "keystoneLevel": fight.get("keystoneLevel"),
                            "dungeonPulls": fight.get("dungeonPulls"),
                        }
                    )
                    count += 1
        seenCodes.add(code)

        if foundFightLimit > 0 and count >= foundFightLimit:
            print(f"Hit found fight limit of {foundFightLimit}, stopping")
            break

    with open(fightsFilePath, "w") as fightsFile:
        json.dump(results, fightsFile, indent=2)


def fetchEvents(
    accessToken: str, code: str, fightIDs: list[int], useFilter: bool, startTime: float, endTime: float = 0
) -> Dict[str, Any]:
    """Fetches events from a report and fight matching the report code and fight ID.

    Args:
        accessToken (str): WarcraftLogs API access token.
        code (str): Report code.
        fightIDs (list[int]): Fight IDs in the report.
        useFilter (bool): If true, applybuff and removebuff events will be included.
        startTime (float): Start time to limit the events to.
        endTime (float, optional): End time to limit the events to. Defaults to 0.

    Returns:
        Dict[str, Any]: Found events.
    """

    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    if useFilter:
        filterExpression = 'ability.id != 1 AND (source.rawDisposition = "enemy" OR ability.id = 181089) AND (type = "begincast" OR type = "cast" OR type = "applybuff" OR type = "removebuff")'
        dataType = "All"
    else:
        filterExpression = ""
        dataType = "Casts"

    variables = {
        "code": code,
        "fightIDs": fightIDs,
        "startTime": startTime,
        "endTime": endTime,
        "filterExpression": filterExpression,
        "dataType": dataType,
    }

    return executeQueryWithRetry(accessToken, fetchEventsQuery, variables)


def fetchAndSaveEvents(
    zoneID: int,
    encounterID: int,
    difficulty: DifficultyType,
    overwriteExisting: bool = False,
):
    """Fetches and saves events for a raid encounter using the fights file corresponding to the zone ID, encounter ID,
    and difficulty type. Each fight's events are saved in a separate file.

    Args:
        zoneID (int): WarcraftLogs API zone ID for the dungeon.
        encounterID (int): Encounter ID for the boss (Translates to dungeonEncounterID in game).
        difficulty (DifficultyType): Difficulty type fights were filtered by.
        overwriteExisting (bool, optional): Whether to overwrite the events files. Defaults to False.
    """

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
                    result = fetchEvents(token, code, [fightID], True, startTime)
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


def fetchAndSaveEventsForDungeon(
    zoneID: int,
    encounterID: int,
    dungeonEncounterID: int,
    overwriteExisting: bool = False,
):
    """Fetches and saves events for a dungeon encounter using the fights file corresponding to the zone ID, encounter
    ID, and dungeon encounter ID. Each fight's events are saved in a separate file.

    Args:
        zoneID (int): WarcraftLogs API zone ID for the dungeon.
        encounterID (int): Encounter ID for the boss (Translates to dungeonEncounterID in game).
        dungeonEncounterID (int): The WarcraftLogs dungeon encounter ID (doesn't translate to anything in game?)
        overwriteExisting (bool, optional): Whether to overwrite the events files. Defaults to False.
    """

    fightsFilePath = getFightsFilePath(zoneID, DifficultyType.Dungeon, dungeonEncounterID)

    if not fightsFilePath.exists():
        print(f"No fights file for zoneID:{zoneID}, encounterID:{encounterID}, dungeonEncounterID:{dungeonEncounterID}")
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

        dungeonPulls = fightObject.get("dungeonPulls")
        for pullID, pull in enumerate(dungeonPulls, start=1):
            if pull.get("encounterID") == encounterID:
                startTime = pull.get("startTime")
                endTime = pull.get("endTime")
                eventsData = []
                eventsFilePath = getEventsFilePathForDungeon(
                    zoneID, dungeonEncounterID, encounterID, code, fightID, pullID
                )
                if not eventsFilePath.exists() or overwriteExisting:
                    try:
                        print(f"Fetching events for code: {code}, fightID: {fightID}, pullID: {pullID}...")
                        nextPageTimestamp = startTime
                        while nextPageTimestamp != None:
                            result = fetchEvents(token, code, [fightID], True, nextPageTimestamp, endTime)
                            currentEventsData = result["reportData"]["report"]["events"]["data"]
                            count = len(currentEventsData)
                            print(f"Found {count} events")
                            if count > 0:
                                eventsData.extend(currentEventsData)
                            nextPageTimestamp = result["reportData"]["report"]["events"]["nextPageTimestamp"]

                    except Exception as e:
                        print(f"Error fetching events for: {code}, fightID: {fightID}, pullID: {pullID}: {e}")
                        return

                if len(eventsData) > 0:
                    with open(eventsFilePath, "w") as eventsFile:
                        json.dump(
                            {"startTime": startTime, "endTime": endTime, "pullID": pullID, "events": eventsData},
                            eventsFile,
                            indent=2,
                        )


def fetchReportsComplex(
    accessToken: str,
    page: int,
    zoneID: int,
    encounterID: int,
    difficulty: DifficultyType,
    killType: KillType,
    reportLimit: int = 0,
) -> Dict[str, Any]:
    """Currently unused due to high query complexity.

    Args:
        accessToken (str): WarcraftLogs API access token.
        page (int): Current page for the query.
        zoneID (int): WarcraftLogs API zone ID for the raid or dungeon.
        encounterID (int):Encounter ID for the boss or WarcraftLogs dungeon encounter ID if fetching for a dungeon.
        difficulty (DifficultyType): Difficulty type to filter fights by.
        killType (KillType): Kill type to filter fights by.
        reportLimit (int, optional): Upper limit on the number of reports per page. Defaults to 0.

    Returns:
        Dict[str, Any]: Found reports
    """

    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {accessToken}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)
    query = """
    query (
        $page: Int!
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

    return executeQueryWithRetry(accessToken, query, variables)
