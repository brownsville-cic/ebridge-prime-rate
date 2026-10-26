"""Refresh prime.json from the Fed's H.15 bank prime loan rate (FRED DPRIME).

Run by .github/workflows/update-prime.yml on weekdays. Writes prime.json only
when the rate changes or the last check is a week old (the weekly write keeps
GitHub from pausing the schedule after 60 days without commits).
Exits non-zero on a bad download, so GitHub emails a failure notice.
"""
import csv
import datetime
import io
import json
import os
import sys
import urllib.request

SERIES_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DPRIME&cosd={start}"
OUT = "prime.json"
HEARTBEAT_DAYS = 7


def fetch_rows():
    start = (datetime.date.today() - datetime.timedelta(days=730)).isoformat()
    # keep the default User-Agent: FRED's firewall drops custom ones
    with urllib.request.urlopen(SERIES_URL.format(start=start), timeout=30) as res:
        text = res.read().decode("utf-8")
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        value = (row.get("DPRIME") or "").strip()
        if value and value != ".":  # holidays come through blank
            rows.append((row["observation_date"], float(value)))
    return rows


def main():
    rows = fetch_rows()
    if not rows:
        sys.exit("FRED returned no DPRIME observations")

    observed, rate = rows[-1]
    if not 1 <= rate <= 20:
        sys.exit(f"Prime rate {rate} looks wrong; not publishing it")

    # effective date = first day of the current run of this rate
    effective = observed
    for date, value in reversed(rows):
        if value != rate:
            break
        effective = date

    today = datetime.date.today().isoformat()
    try:
        with open(OUT) as f:
            old = json.load(f)
    except (FileNotFoundError, ValueError):
        old = {}

    changed = old.get("primeRate") != rate or old.get("effective") != effective
    last_check = datetime.date.fromisoformat(old.get("checked", "2000-01-01"))
    stale = (datetime.date.today() - last_check).days >= HEARTBEAT_DAYS
    if not changed and not stale:
        print(f"Prime unchanged at {rate:.2f}% (effective {effective}); nothing to write")
        return

    data = {
        "primeRate": rate,
        "effective": effective,
        "observed": observed,
        "checked": today,
        "source": "Federal Reserve H.15 bank prime loan rate (FRED series DPRIME)",
        "sourceUrl": "https://fred.stlouisfed.org/series/DPRIME",
    }
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    message = (f"Prime rate {rate:.2f}% effective {effective}" if changed
               else f"Weekly check: prime still {rate:.2f}%")
    print(message)
    if os.environ.get("RUNNER_TEMP"):
        with open(os.path.join(os.environ["RUNNER_TEMP"], "commit-msg"), "w") as f:
            f.write(message + "\n")


if __name__ == "__main__":
    main()
