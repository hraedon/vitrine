#!/usr/bin/env python3
"""Author the Plan 027 WI-4a road-death cards from the source table (one-shot).

The thirteen ``us-<decade>-traffic-death-rate`` facts were written into the
room files by this script, not typed, on the same terms as
``scripts/niaaa_alcohol_cards.py``: every numeral it writes is read from
``scripts/fhwa_traffic_deaths_extract.py``'s parse of FHWA Table FI-200 and
asserted against it before anything is written, and the script is committed so
that those assertions stay inspectable. The prose around the numerals is
authored here; the numbers are not.

Each decade takes its first published year (1900, 1910, …), the convention the
cigarette and alcohol cards already use. FI-200 is continuous from 1900, so
unlike the alcohol series there is no decade without an anchor.

Re-running is safe: a room that already carries its card is left alone.
Requires the gitignored ``samples/`` archive, so it is a local tool; the
CI-runnable half is ``tests/test_traffic_deaths.py``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fhwa_traffic_deaths_extract as ex

REPO = Path(__file__).resolve().parent.parent
DECADES = [d for d in range(1900, 2030, 10)]

NOTES = {
    1900: (
        "The earliest year FHWA publishes, and the thinnest: the rate rests "
        "on 36 recorded deaths against an estimated 100 million "
        "vehicle-miles. It is a real published figure, not a reconstruction, "
        "but the exposure behind it is tiny and the travel estimate is a "
        "back-cast."
    ),
    1910: (
        "Just past the worst year in the whole table: the rate peaked in 1909 "
        "at 45.33, as cars reached ordinary streets faster than anything that "
        "later made them survivable."
    ),
    1920: (
        "Twelve thousand people a year were being killed by then. The rate "
        "was already falling, because travel was growing faster than the toll."
    ),
    1930: (
        "Thirty-one thousand deaths, with no federal crash standards for "
        "cars, no seat belts and no national safety agency."
    ),
    1940: (
        "Wartime rationing cut driving sharply — vehicle-miles fell 38 "
        "percent between 1941 and 1943 — and deaths fell almost exactly as "
        "far, by 40 percent. The rate barely moved: 11.43 in 1941, 10.92 in "
        "1943. Fewer people died because less driving happened, not because "
        "driving got safer."
    ),
    1950: (
        "Absolute deaths were close to where they had been in 1930 — 33,186 "
        "against 31,204 — while travel had more than doubled, from 206,320 "
        "million vehicle-miles to 458,246 million. The falling rate is that "
        "denominator, not fewer funerals."
    ),
    1960: (
        "Before the National Traffic and Motor Vehicle Safety Act of 1966, "
        "the federal government set no crash standards for cars at all."
    ),
    1970: (
        "Absolute deaths peaked in this decade, at 55,600 in 1972 — the "
        "highest figure in the table's 124 years."
    ),
    1980: (
        "Seat-belt laws spread across the states through this decade, and the "
        "rate fell from 3.35 to 2.08 across it."
    ),
    1990: (
        "The rate crosses below 2 deaths per 100 million vehicle-miles the "
        "following year, 1991, and never rises above it again."
    ),
    2000: (
        "Travel passed 2.7 trillion vehicle-miles a year while deaths stayed "
        "near 42,000: the rate falls because the denominator grows."
    ),
    2010: (
        "Absolute deaths, at 32,999, were lower than in any year since 1949. "
        "The rate would fall a little further still, to its 124-year low of "
        "1.08 in 2014."
    ),
    2020: (
        "The pandemic year. Travel collapsed but deaths did not fall with it, "
        "so the rate rose to 1.34 — its highest since 2007."
    ),
}


def main() -> None:
    rows = ex.parse_fi200()
    ex.check_arithmetic(rows)

    # every numeral quoted in the prose above, checked against the table
    assert int(rows[1900]["fatalities"]) == 36 and int(rows[1900]["vmt"]) == 100
    peak_rate_year = max(rows, key=lambda y: rows[y]["rate"])
    assert peak_rate_year == 1909 and rows[1909]["rate"] == 45.33, peak_rate_year
    assert rows[1941]["rate"] == 11.43 and rows[1943]["rate"] == 10.92
    assert round(1 - rows[1943]["vmt"] / rows[1941]["vmt"], 2) == 0.38
    assert round(1 - rows[1943]["fatalities"] / rows[1941]["fatalities"], 2) == 0.40
    assert int(rows[1930]["vmt"]) == 206320 and int(rows[1950]["vmt"]) == 458246
    assert rows[1950]["vmt"] / rows[1930]["vmt"] > 2.0
    assert int(rows[1950]["fatalities"]) == 33186 and int(rows[1930]["fatalities"]) == 31204
    peak_deaths_year = max(rows, key=lambda y: rows[y]["fatalities"])
    assert peak_deaths_year == 1972 and int(rows[1972]["fatalities"]) == 55600
    assert rows[1980]["rate"] == 3.35 and rows[1990]["rate"] == 2.08
    assert min(y for y in rows if rows[y]["rate"] < 2.0) == 1991
    assert all(rows[y]["rate"] < 2.0 for y in range(1991, max(rows) + 1))
    assert int(rows[2000]["vmt"]) > 2_700_000
    assert int(rows[2010]["fatalities"]) == 32999
    assert max(y for y in rows if rows[y]["fatalities"] <= 32999 and y < 2010) == 1949
    low_year = min(rows, key=lambda y: rows[y]["rate"])
    assert low_year == 2014 and rows[2014]["rate"] == 1.08, low_year
    assert rows[2020]["rate"] == 1.34
    assert all(rows[2020]["rate"] > rows[y]["rate"] for y in range(2008, 2020))

    for decade in DECADES:
        row = rows[decade]
        fid = f"us-{decade}s-traffic-death-rate"
        path = REPO / "data" / "us" / f"{decade}s.toml"
        text = path.read_text()
        if f'id = "{fid}"' in text:
            print(f"{decade}s: already present, left alone")
            continue
        block = f'''[[fact]]
id = "{fid}"
quantity = {row["rate"]:.2f}
panel = "day"
label = "Road deaths per 100 million vehicle-miles, {decade}"
value = "{row["rate"]:.2f} deaths per 100 million vehicle-miles travelled"
unit = "deaths per 100 million vehicle-miles travelled"
price_year = {decade}
source = "fhwa-fi200-2023"
tier = "A"
notes = "{NOTES[decade]}"
assumptions = ["composite-family"]
'''
        anchor = f'id = "us-{decade}s-ethanol-per-capita"'
        i = text.index(anchor)
        m = re.compile(r"\n\n(?=\[\[fact\]\]|# )").search(text, i)
        if m is None:
            raise SystemExit(f"{decade}s: could not find the end of the alcohol block")
        cut = m.start() + 1
        path.write_text(text[:cut] + "\n" + block + text[cut:])
        print(f"{decade}s: inserted {fid}  (rate {row['rate']:.2f})")


if __name__ == "__main__":
    main()
