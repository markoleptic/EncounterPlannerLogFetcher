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

## Print a list of report IDs from Warcraft Logs

```
[...document.querySelectorAll("a[href*='/reports/']")].map(a => {
    let match = a.href.match(/\/reports\/([A-Za-z0-9]+)/);
    return match ? match[1] : null;})
.filter(id => id !== null).join("\",\"");
```
