# Encounter Planner Log Fetcher

## Usage

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
.venv/bin/python -m src.main
```

You will need a WarcraftLogs API client ID and client secret available at https://www.warcraftlogs.com/api/clients/.
Create a `.env` file with the both:

```
CLIENT_ID={client ID from WarcraftLogs}
CLIENT_SECRET={client secret from WarcraftLogs}
```

`fetchAndSaveReports(44, 100, 20)` fetches most recent reports from zone 44 (Manaforge Omega), 100 reports per page, 20 pages.

`fetchAndSaveFights(44, 3134, DifficultyType.Mythic, KillType.Kills, True, 1)` uses the reports file to find fights for Nexus-King Salhadaar that are mythic difficulty, only kills (no wipes), overrides existing fights files, and limits
the number of found fights to one.
The fights are saved to `fights/{zoneID}_{encounterID}_{difficulty}.json`.

`fetchAndSaveEvents(44, 3134, DifficultyType.Mythic, True)` uses the fights file to fetch all events from the fights.
The events for each fight are saved to `events/{zoneID}/{difficulty}/{encounterID}/{zoneID}_{encounterID}_{difficulty}.json`.

## Print a list of report IDs from Warcraft Logs

```
[...document.querySelectorAll("a[href*='/reports/']")].map(a => {
    let match = a.href.match(/\/reports\/([A-Za-z0-9]+)/);
    return match ? match[1] : null;})
.filter(id => id !== null).join("\",\"");
```
