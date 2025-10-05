# Encounter Planner Log Fetcher

## Usage

`.venv/bin/python -m src.main`

## Print a list of report IDs from Warcraft Logs

```
[...document.querySelectorAll("a[href*='/reports/']")].map(a => {
    let match = a.href.match(/\/reports\/([A-Za-z0-9]+)/);
    return match ? match[1] : null;})
.filter(id => id !== null).join("\",\"");
```
