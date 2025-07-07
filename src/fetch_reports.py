import json
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from src.enums import DifficultyType, KillType
from typing import Any, Dict

from src.utility import get_access_token, get_events_path, get_fights_path, get_reports_path


def fetch_reports(
    access_token: str,
    page: int,
    zone_id: int,
    report_limit: int = 0,
) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query (
        $page: Int!,
        $zone_id: Int!
        $report_limit: Int
    ) {
        reportData {
            reports(page: $page, zoneID: $zone_id, limit: $report_limit) {
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
        "zone_id": zone_id,
        "report_limit": report_limit,
    }

    return client.execute(gql(query), variables)


def fetch_and_save_reports(zone_id: int = 44, report_limit: int = 100, max_pages: int = 10):
    token = get_access_token()
    page = 1
    report_codes = []

    while page <= max_pages:
        try:
            print(f"Fetching page {page}...")
            result = fetch_reports(token, page, zone_id, report_limit)

            reports_data = result["reportData"]["reports"]["data"]
            print(f"Found {len(reports_data)} reports on page {page}")

            for report in reports_data:
                code = report["code"]
                report_codes.append(code)

            if not result["reportData"]["reports"]["has_more_pages"]:
                print("No more pages.")
                break

            page += 1
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    path = get_reports_path() / f"{zone_id}.json"
    with open(path, "w") as report_file:
        json.dump(
            {"zone_id": zone_id, "last_page": page, "codes": report_codes},
            report_file,
            indent=2,
        )


def fetch_fights_from_report(
    access_token: str,
    code: str,
    encounter_id: int,
    difficulty: DifficultyType,
    kill_type: KillType,
) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query (
        $code: String
        $difficulty: Int
        $encounter_id: Int
        $kill_type: KillType
    ) {
        reportData {
            report(code: $code) {
                fights(
                    difficulty: $difficulty
                    encounterID: $encounter_id
                    killType: $kill_type
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
        "encounter_id": encounter_id,
        "difficulty": difficulty,
        "kill_type": kill_type,
    }

    return client.execute(gql(query), variables)


def fetch_and_save_fights(
    zone_id: int,
    encounter_id: int,
    difficulty: DifficultyType,
    kill_type: KillType,
    report_limit: int,
    max_pages: int,
):
    token = get_access_token()
    results = []

    with open(get_reports_path() / f"{zone_id}.json") as reports_file:
        report_codes = json.load(reports_file)
        all_codes = report_codes["codes"]

        for code in all_codes:
            try:
                print(f"Fetching fights for {code}...")
                result = fetch_fights_from_report(token, code, encounter_id, difficulty, kill_type)

                fights_data = result["reportData"]["report"]["fights"]
                print(f"Found {len(fights_data)} fights for {code}")

                for fight_data in fights_data:
                    fight_id = fight_data["id"]
                    start_time = fight_data["startTime"]

                    if fight_id and start_time:
                        results.append(
                            {
                                "code": code,
                                "id": fight_id,
                                "start_time": start_time,
                                "fight_percentage": fight_data["fightPercentage"],
                                "keystone_level": fight_data["keystoneLevel"] or None,
                                "phase_transitions": fight_data["phaseTransitions"] or None,
                            }
                        )

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                continue

    with open(get_fights_path() / f"{zone_id}_{encounter_id}_{difficulty}.json", "w") as fight_id_file:
        json.dump(
            results,
            fight_id_file,
            indent=2,
        )


def fetch_fight_from_report(access_token: str, code: str, fight_id: int) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query ($code: String, $fight_ids: [Int]) {
        reportData {
            report(code: $code) {
                fights(fightIDs: $fight_ids) {
                    id
                    startTime
                }
            }
        }
    }"""

    variables = {
        "code": code,
        "fight_ids": [fight_id],
    }

    return client.execute(gql(query), variables)


def fetch_events(access_token: str, code: str, fight_ids: list[int], start_time: float) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query($code: String, $fight_ids: [Int], $start_time: Float) {
        reportData {
            report(code: $code) {
                events(
                    fightIDs: $fight_ids
                    dataType: Casts
                    hostilityType: Enemies
                    limit: 10000
                    startTime: $start_time
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
        "fight_ids": fight_ids,
        "start_time": start_time,
    }

    return client.execute(gql(query), variables)


def fetch_and_save_events(zone_id: int, encounter_id: int, difficulty: DifficultyType):
    token = get_access_token()

    with open(get_fights_path() / f"{zone_id}_{encounter_id}_{difficulty}.json") as fights_file:
        fight_objects = json.load(fights_file)

        for fight_object in fight_objects:
            code = fight_object["code"]
            fight_id = fight_object["id"]
            fight_start_time = fight_object["start_time"]
            start_time = 0.0
            events_data = []
            try:
                print(f"Fetching events for {code}, {fight_id}...")

                while True:
                    result = fetch_events(token, code, [fight_id], start_time)
                    events_data_current = result["reportData"]["report"]["events"]["data"]
                    count = len(events_data_current)
                    print(f"Found {count} events for {code}, {fight_id}")

                    if count > 0:
                        events_data.extend(events_data_current)

                    next_page = result["reportData"]["report"]["events"]["nextPageTimestamp"]
                    if next_page:
                        start_time = next_page
                    else:
                        break

                if len(events_data) > 0:
                    path = get_events_path() / f"{zone_id}_{encounter_id}_{difficulty}_{code}_{fight_id}.json"
                    with open(path, "w") as events_file:
                        json.dump(
                            {
                                "start_time": fight_start_time,
                                "events": events_data,
                            },
                            events_file,
                            indent=2,
                        )

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                continue


def fetch_reports_complex(
    access_token: str,
    page: int,
    zone_id: int,
    encounter_id: int,
    difficulty: DifficultyType,
    kill_type: KillType,
    report_limit: int = 0,
) -> Dict[str, Any]:
    transport = RequestsHTTPTransport(
        url="https://www.warcraftlogs.com/api/v2/client",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = """
    query (
        $page: Int!,
        $zone_id: Int!
        $encounter_id: Int!
        $difficulty: Int!
        $kill_type: KillType!
        $report_limit: Int
    ) {
        reportData {
            reports(zoneID: $zone_id, page: $page, limit: $report_limit) {
                current_page
                data {
                    code
                    startTime
                    endTime
                    fights(
                        encounterID: $encounter_id
                        difficulty: $difficulty
                        killType: $kill_type
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
        "zone_id": zone_id,
        "encounter_id": encounter_id,
        "difficulty": difficulty,
        "kill_type": kill_type,
        "report_limit": report_limit,
    }

    return client.execute(gql(query), variables)
