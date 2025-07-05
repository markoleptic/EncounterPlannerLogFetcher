from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from src.enums import DifficultyType, KillType
from typing import Any, Dict


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
