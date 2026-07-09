#!/usr/bin/env python3
"""Extract two CES manufacturing earnings series from the BLS Public Data API.

Emits:
* ``data/series/hourly-earnings-manufacturing.toml``  (CES3000000008,
  source ``fred-ces-manuf-earnings``)
* ``data/series/weekly-earnings-manufacturing.toml``  (CES3000000030,
  source ``fred-ces-manuf-weekly-earnings`` — a NEW source; see data/sources.toml)

Both are CES production/nonsupervisory manufacturing employees, monthly. The
API does not return M13 annual rows for these CES series, so we annualize
ourselves as the arithmetic mean of the 12 monthly values for each complete year
(Jan-Dec present), 1939-2024. Both are wage RATES in dollars -> ``values``
(floats).

The existing fact ``us-1950s-hourly-earnings-manufacturing`` (amount_minor 132 =
$1.32) was itself computed by averaging the 12 monthly 1950 values, so this
series reproduces it exactly. Its drift branch keys on ``quantity`` (None), so
no drift failure can arise; we still verify 1950 ~= $1.32 by eye.

FRED fredgraph.csv is network-blocked from this environment, so the BLS API
(which feeds FRED) is the source of record. Chunked at 10 years/request.
"""

from __future__ import annotations

import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "series"
API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
START_YEAR, END_YEAR = 1939, 2024
CHUNK = 10

SERIES = [
    {
        "seriesid": "CES3000000008",
        "id": "hourly-earnings-manufacturing",
        "label": "Average hourly earnings, manufacturing production/nonsupervisory",
        "source": "fred-ces-manuf-earnings",
        "unit": "USD per hour, nominal (annual mean of 12 monthly values)",
        "notes": (
            "BLS CES series CES3000000008 (Average Hourly Earnings of Production and "
            "Nonsupervisory Employees, Manufacturing), monthly, annualized as the mean "
            "of 12 months. Predecessor to AHETPI (which is total private, 1964->)."
        ),
    },
    {
        "seriesid": "CES3000000030",
        "id": "weekly-earnings-manufacturing",
        "label": "Average weekly earnings, manufacturing production/nonsupervisory",
        "source": "fred-ces-manuf-weekly-earnings",
        "unit": "USD per week, nominal (annual mean of 12 monthly values)",
        "notes": (
            "BLS CES series CES3000000030 (Average Weekly Earnings of Production and "
            "Nonsupervisory Employees, Manufacturing), monthly, annualized as the mean "
            "of 12 months. Weekly x 52 gives annual earnings without smuggling in a "
            "weekly-hours assumption."
        ),
    },
]


def _pull_months(seriesid: str, key: str | None) -> dict[int, list[float]]:
    """Return year->list-of-monthly-values for the whole window."""
    months: dict[int, list[float]] = defaultdict(list)
    for start in range(START_YEAR, END_YEAR + 1, CHUNK):
        end = min(start + CHUNK - 1, END_YEAR)
        body = {
            "seriesid": [seriesid],
            "startyear": str(start),
            "endyear": str(end),
            "calculations": False,
            "annualaverage": False,
        }
        # BLS API v2 requires the registration key in the JSON BODY (not a
        # header); placed in a header it is silently ignored and the request
        # falls under the 25/day unregistered cap instead of 500/day.
        if key:
            body["registrationkey"] = key
        headers = {"Content-Type": "application/json"}
        last_err = ""
        for _attempt in range(3):
            try:
                r = requests.post(API_URL, json=body, headers=headers, timeout=60)
                if r.status_code == 429:
                    time.sleep(15)
                    continue
                data = r.json()
                if data.get("status") != "REQUEST_SUCCEEDED":
                    last_err = str(data.get("message", data))
                    time.sleep(3)
                    continue
                for s in data["Results"]["series"]:
                    for obs in s["data"]:
                        period = obs.get("period", "")
                        # Keep monthly M01-M12; skip M13 (annual) and anything else.
                        if not (period.startswith("M") and period != "M13"):
                            continue
                        months[int(obs["year"])].append(float(obs["value"]))
                break
            except (requests.RequestException, ValueError, KeyError) as exc:
                last_err = repr(exc)
                time.sleep(3)
        else:
            raise RuntimeError(f"BLS API {seriesid} chunk {start}-{end} failed: {last_err}")
        print(f"  {seriesid} {start}-{end}: ok", file=sys.stderr)
        time.sleep(1)
    return months


def _annualize(months: dict[int, list[float]]) -> dict[int, float]:
    out: dict[int, float] = {}
    for y, obs in months.items():
        if len(obs) == 12:  # complete year only
            out[y] = round(sum(obs) / 12.0, 4)
    return out


def _emit(spec: dict, values: dict[int, float]) -> Path:
    yrs = sorted(values)
    lines = [
        "# Auto-generated by scripts/bls_ces_extract.py from the BLS Public Data API",
        f"# BLS series {spec['seriesid']}, monthly; annualized as the mean of 12 months.",
        f"# Coverage: {yrs[0]}-{yrs[-1]} (complete years only).",
        "",
        "[[series]]",
        f'id = "{spec["id"]}"',
        f'label = "{spec["label"]}"',
        f'source = "{spec["source"]}"',
        'tier = "A"',
        f'unit = "{spec["unit"]}"',
        'population = "Production and nonsupervisory employees in manufacturing"',
        f'notes = "{spec["notes"]}"',
        "",
        "[series.values]",
    ]
    for y in yrs:
        lines.append(f"{y} = {values[y]:.4f}")
    lines.append("")
    out = OUT_DIR / f'{spec["id"]}.toml'
    out.write_text("\n".join(lines))
    return out


def main() -> int:
    key = os.environ.get("BLS_API_KEY")
    for spec in SERIES:
        months = _pull_months(spec["seriesid"], key)
        values = _annualize(months)
        if not values:
            print(f"ERROR: no data for {spec['seriesid']}", file=sys.stderr)
            return 1
        path = _emit(spec, values)
        yrs = sorted(values)
        gaps = sorted(set(range(yrs[0], yrs[-1] + 1)) - set(yrs))
        for y in (yrs[0], 1950, 1980, 2010, yrs[-1]):
            print(f"  {spec['id']}[{y}] = {values[y]:.4f}")
        print(f"{spec['id']}: {len(values)} years ({yrs[0]}-{yrs[-1]})"
              + (f", gaps: {gaps}" if gaps else "")
              + f" -> {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
