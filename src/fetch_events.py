from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from typing import Any, Dict


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
