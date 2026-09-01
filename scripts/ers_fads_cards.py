#!/usr/bin/env python3
"""Author the Plan 027 WI-6a food-availability cards (one-shot).

One card per (commodity, decade) for the four arc-group commodities, on the
same terms as the earlier generators: values are read from
``scripts/ers_fads_extract.py``'s parse of the ERS workbooks and asserted
before writing, and every numeral quoted in a card's prose is checked against
the parse.

Each decade takes its first published year, so a commodity's cards begin where
its sheet begins — broccoli and peppers at 1960, avocados and grapes at 1970 —
and no decade before that gets an invented one.

Re-running is safe: a room that already carries a card is left alone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ers_fads_extract as ex

REPO = Path(__file__).resolve().parent.parent

# what each card says beyond its number; the {first}/{last} figures are
# substituted from the parse, never typed
SHARED = (
    "Food availability, not intake: production plus imports less exports and "
    "non-food use, over population. Farm weight, as ERS publishes it."
)
COMMODITY_NOTE = {
    "broccoli": "Fresh broccoli.",
    "bell-peppers": "Fresh bell peppers.",
    "avocados": "Fresh avocados.",
    "grapes": "Fresh grapes.",
}
LABEL = {
    "broccoli": "Broccoli available per person",
    "bell-peppers": "Bell peppers available per person",
    "avocados": "Avocados available per person",
    "grapes": "Grapes available per person",
}


def main() -> None:
    parsed = {slug: ex.parse(wb, sheet)[0]
              for slug, (wb, sheet, _l) in ex.COMMODITIES.items()}

    # the figures quoted in the arc caveats, asserted here so a caveat cannot
    # drift from the data it describes
    assert parsed["broccoli"][1960] == 0.40 and parsed["broccoli"][2022] == 5.24
    assert parsed["avocados"][1970] == 0.45 and parsed["avocados"][2017] == 8.06
    assert parsed["bell-peppers"][1960] == 2.08
    assert parsed["grapes"][1970] == 2.92

    written = 0
    for slug, values in parsed.items():
        first_year = min(values)
        for decade_start in range(1900, 2030, 10):
            decade = f"{decade_start}s"
            year = next((y for y in range(decade_start, decade_start + 10)
                         if y in values), None)
            if year is None:
                continue
            fid = f"us-{decade}-availability-{slug}"
            path = REPO / "data" / "us" / f"{decade}.toml"
            text = path.read_text()
            if f'id = "{fid}"' in text:
                continue
            ratio = values[year] / values[first_year]
            shape = (
                f" {ratio:.1f} times the {first_year} figure."
                if year != first_year and ratio >= 1.5
                else " The first year ERS publishes for this commodity."
                if year == first_year
                else ""
            )
            note = f"{COMMODITY_NOTE[slug]} {SHARED}{shape}"
            block = f'''[[fact]]
id = "{fid}"
quantity = {values[year]}
panel = "table"
label = "{LABEL[slug]}, {year}"
value = "{values[year]} pounds per person per year"
unit = "pounds per person per year (farm weight)"
price_year = {year}
source = "usda-ers-fads"
tier = "A"
notes = "{note}"
assumptions = ["composite-family"]
'''
            anchor = f'id = "us-{decade}-ethanol-per-capita"'
            i = text.index(anchor)
            m = re.compile(r"\n\n(?=\[\[fact\]\]|# )").search(text, i)
            if m is None:
                raise SystemExit(f"{decade}: no insertion point")
            cut = m.start() + 1
            path.write_text(text[:cut] + "\n" + block + text[cut:])
            written += 1
            print(f"  {decade} {slug:14} {values[year]:>6.2f} lb  ({year})")
    print(f"\n{written} card(s) written")


if __name__ == "__main__":
    main()
