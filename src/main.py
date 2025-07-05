import json
from src.fetch_events import fetch_events
from src.fetch_reports import (
    fetch_fight_from_report,
    fetch_fights_from_report,
    fetch_reports,
)
from src.enums import DifficultyType, KillType
from src.utility import (
    get_access_token,
    get_fights_path,
    get_reports_path,
    get_events_path,
)
from collections import defaultdict


def fetch_reports_by_zone_id(zone_id: int = 44, report_limit: int = 100, max_pages: int = 10):
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

    with open(get_reports_path() / f"{zone_id}.json", "w") as report_file:
        json.dump(
            {"zone_id": zone_id, "last_page": page, "codes": report_codes},
            report_file,
            indent=2,
        )


def fetch_fight_ids_from_report_ids(
    zone_id: int = 44,
    encounter_id: int = 3132,
    difficulty: DifficultyType = DifficultyType.Heroic,
    kill_type: KillType = KillType.Kills,
    report_limit: int = 100,
    max_pages: int = 10,
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


def fetch_events_from_fight_ids(
    zone_id: int = 44, encounter_id: int = 3132, difficulty: DifficultyType = DifficultyType.Heroic
):
    token = get_access_token()

    with open(get_fights_path() / f"{zone_id}_{encounter_id}_{difficulty}.json") as fights_file:
        fight_ids = json.load(fights_file)

        for fight_id_object in fight_ids:
            code = fight_id_object["code"]
            fight_id = fight_id_object["id"]
            fight_start_time = fight_id_object["start_time"]
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
                    with open(
                        get_events_path() / f"{zone_id}_{encounter_id}_{difficulty}_{code}_{fight_id}.json",
                        "w",
                    ) as events_file:
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


if __name__ == "__main__":
    exit()
