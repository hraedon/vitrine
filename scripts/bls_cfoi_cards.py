#!/usr/bin/env python3
"""Author the Plan 027 WI-4b workplace-death cards (one-shot).

Four cards, on the same terms as the alcohol and road-death generators: every
numeral is read from ``scripts/bls_cfoi_rates_extract.py``'s parse of the BLS
workbooks and asserted before writing, and the script is committed so those
assertions stay inspectable.

Only three decades can carry a value, because only three decades have one. The
fourth card is the 1990s, and it is a gap: the Census of Fatal Occupational
Injuries began covering all fifty states in 1992, so for the nine decades
before it the United States kept no federal count of the people killed at
work — and the rates CFOI did publish from 1992 to 2005 were computed on an
employment basis that BLS replaced in 2006, so they are a different measure
and cannot be chained onto this one.

Re-running is safe: a room that already carries its card is left alone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bls_cfoi_rates_extract as ex

REPO = Path(__file__).resolve().parent.parent

ANCHORS = {"2000s": 2006, "2010s": 2010, "2020s": 2020}
GAP_DECADE = "1990s"

NOTES = {
    "2000s": (
        "The first year the federal government published this measure. Before "
        "2006 the rate was computed against employment rather than hours "
        "worked, and before 1992 there was no federal census of workplace "
        "deaths at all — so 2006 is where the line can start, not where the "
        "risk began."
    ),
    "2010s": (
        "The rate has moved inside a narrow band since the measure began: "
        "between 3.3 and 4.2 across nineteen years, with no trend the record "
        "can call a fall."
    ),
    "2020s": (
        "The pandemic year. The rate rose to 3.7 by 2022 before easing to 3.3 "
        "in 2024, the joint-lowest figure in the series."
    ),
    GAP_DECADE: (
        "The Census of Fatal Occupational Injuries has covered all fifty "
        "states and the District of Columbia only since 1992. For the nine "
        "decades before that the United States kept no federal count of the "
        "people killed at work; the century-long figures usually quoted come "
        "from a private safety council's estimates, not a government census. "
        "The rates CFOI itself published from 1992 to 2005 were computed "
        "against employment rather than hours worked, and BLS replaced that "
        "basis in 2006 — so they measure something else and are not shown on "
        "the same axis. This gap is not an archive limitation. It is the "
        "absence of the counting."
    ),
}

GAP_VALUE = (
    "no reliable record — the federal census of workplace deaths began in 1992, "
    "and its rate basis changed in 2006"
)


def main() -> None:
    rates = ex.parse_all()

    # every numeral quoted in the prose above, checked against the parse
    assert min(rates) == 2006 and ex.CFOI_BEGINS == 1992
    assert rates[2006] == 4.2 and rates[2010] == 3.6 and rates[2020] == 3.4
    assert rates[2022] == 3.7 and rates[2024] == 3.3
    assert min(rates.values()) == 3.3 and max(rates.values()) == 4.2
    assert len(rates) == 19, len(rates)
    assert rates[2024] == min(rates.values()), "2024 is not the joint-lowest"

    for decade in [*ANCHORS, GAP_DECADE]:
        fid = f"us-{decade}-workplace-death-rate"
        path = REPO / "data" / "us" / f"{decade}.toml"
        text = path.read_text()
        if f'id = "{fid}"' in text:
            print(f"{decade}: already present, left alone")
            continue
        if decade == GAP_DECADE:
            block = f'''[[fact]]
id = "{fid}"
panel = "day"
label = "Deaths at work per 100,000 workers, 1990s"
value = "{GAP_VALUE}"
unit = "fatal work injuries per 100,000 full-time-equivalent workers"
source = "bls-cfoi-hours-based-rates"
tier = "A"
notes = "{NOTES[decade]}"
assumptions = ["composite-family"]
'''
        else:
            year = ANCHORS[decade]
            block = f'''[[fact]]
id = "{fid}"
quantity = {rates[year]:.1f}
panel = "day"
label = "Deaths at work per 100,000 workers, {year}"
value = "{rates[year]:.1f} fatal work injuries per 100,000 full-time-equivalent workers"
unit = "fatal work injuries per 100,000 full-time-equivalent workers"
price_year = {year}
source = "bls-cfoi-hours-based-rates"
tier = "A"
notes = "{NOTES[decade]}"
assumptions = ["composite-family"]
'''
        anchor = f'id = "us-{decade}-traffic-death-rate"'
        i = text.index(anchor)
        m = re.compile(r"\n\n(?=\[\[fact\]\]|# )").search(text, i)
        if m is None:
            raise SystemExit(f"{decade}: could not find the end of the road-death block")
        cut = m.start() + 1
        path.write_text(text[:cut] + "\n" + block + text[cut:])
        kind = "GAP" if decade == GAP_DECADE else f"{rates[ANCHORS[decade]]:.1f}"
        print(f"{decade}: inserted {fid}  ({kind})")


if __name__ == "__main__":
    main()
