# ebridge-prime-rate

Live prime rate for the eBridge Fund loan calculator on ebridgefund.com.

A GitHub Action (`.github/workflows/update-prime.yml`) runs every weekday. It reads the
Federal Reserve's H.15 bank prime loan rate ([FRED series DPRIME](https://fred.stlouisfed.org/series/DPRIME)),
which moves in step with the WSJ Prime Rate, and writes it to `prime.json`:

```json
{
  "primeRate": 7.0,
  "effective": "2026-09-17",
  "observed": "2026-10-21",
  "checked": "2026-10-26",
  "source": "Federal Reserve H.15 bank prime loan rate (FRED series DPRIME)",
  "sourceUrl": "https://fred.stlouisfed.org/series/DPRIME"
}
```

- `primeRate`: current prime rate, in percent
- `effective`: the date prime moved to this rate (the calculator shows it as "as of")
- `observed`: the latest day FRED has data for
- `checked`: the last time the Action wrote this file

The calculator loads it from
`https://raw.githubusercontent.com/brownsville-cic/ebridge-prime-rate/main/prime.json`.
If that request fails or the value looks wrong, the calculator uses `primeRate` and `primeAsOf`
from its own CONFIG block instead.

This repo is public so the calculator can read the file without a login. It holds only
public Federal Reserve data.

## Upkeep

- **Nothing to do day to day.** The file commits when prime changes, and once a week otherwise
  so GitHub keeps the schedule running.
- **If a run fails**, GitHub emails the person who last edited the workflow. The calculator
  keeps using the last good `prime.json` in the meantime.
- **To refresh by hand:** Actions tab, "Update prime rate", "Run workflow".
