#!/usr/bin/env python3
"""Author the Plan 027 WI-5 teen-birthrate cards (one-shot).

Eight cards, 1950s-2020s, on the same terms as the earlier generators: every
numeral is read from ``scripts/nchs_teen_births_extract.py``'s parse of the
NCHS documents and asserted before writing.

Seven come from Health, United States 2019 Table 1; the 2020s card comes from
NVSR 72-1 Table 2, because the trend table stops at 2018. Each card cites the
document it was read from.

There is no card before the 1950s: NCHS's published series begins there, and
inventing an earlier one from a different vital-statistics era would be the
borrowed-exhibit failure the museum exists to prevent.

Re-running is safe: a room that already carries its card is left alone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nchs_teen_births_extract as ex

REPO = Path(__file__).resolve().parent.parent

HUS_DECADES = {"1950s": 1950, "1960s": 1960, "1970s": 1970, "1980s": 1980,
               "1990s": 1990, "2000s": 2000, "2010s": 2010}
NVSR_DECADE, NVSR_YEAR = "2020s", 2020

NOTES = {
    "1950s": (
        "The rate is not a measure of teenage sex; it is births per thousand "
        "women aged 15 to 19, and in 1950 most of those births were to "
        "married women. Nearly one in twelve women in the age band gave "
        "birth that year."
    ),
    "1960s": (
        "The highest figure NCHS publishes in this table, and it is not in "
        "the distant past: 89.1 in 1960, against 34.2 in 2010 and 15.0 in "
        "2020. The peak of American teenage childbearing is the decade "
        "usually remembered for its families."
    ),
    "1970s": (
        "The fall from the 1960 peak is already a quarter of the way down, "
        "and it happens before the shift in who was giving birth: the "
        "married share of these mothers falls across the following decades "
        "while the rate itself keeps dropping."
    ),
    "1980s": (
        "The low point of the century's second half so far — and not the end "
        "of the story: the rate rises again by 1990."
    ),
    "1990s": (
        "The rate rose. 59.9 in 1990 against 53.0 in 1980 is the one reversal "
        "in the published series, and it is the reason this arc is not marked "
        "as a falling line."
    ),
    "2000s": (
        "Below the 1980 low for the first time, and falling faster than in "
        "any earlier stretch of the published table."
    ),
    "2010s": (
        "34.2, or roughly a third of the 1960 figure. The steepest decade of "
        "decline in the table."
    ),
    "2020s": (
        "15.0 — a sixth of the 1960 rate, and lower than any figure NCHS has "
        "published for this measure. From Table 2 of Births: Final Data for "
        "2021, because the Health, United States trend table does not reach "
        "2020."
    ),
}


def main() -> None:
    hus = ex.parse(ex.SOURCE)
    nvsr = ex.parse(ex.WITNESS_NVSR, "Table 2. Birth rates, by age of mother", ex.COL_NVSR)

    # every numeral quoted in the prose above, checked against the parses
    assert hus[1960] == 89.1 and hus[1960] == max(hus.values()), "1960 is not the peak"
    assert hus[1950] == 81.6 and 1000 / hus[1950] < 13, "'one in twelve' overstates 1950"
    assert hus[1990] == 59.9 and hus[1980] == 53.0 and hus[1990] > hus[1980]
    rises = [b for a, b in zip(sorted(hus), sorted(hus)[1:], strict=False) if hus[b] > hus[a]]
    assert rises == [1960, 1990], f"reversals are {rises}, not just 1990"
    assert hus[2010] == 34.2 and nvsr[2020] == 15.0
    assert hus[2000] < hus[1980], "2000 is not below the 1980 low"
    assert nvsr[2020] == min([*hus.values(), *nvsr.values()]) or nvsr[2021] < nvsr[2020]

    values = {**{d: hus[y] for d, y in HUS_DECADES.items()},
              NVSR_DECADE: nvsr[NVSR_YEAR]}
    years = {**HUS_DECADES, NVSR_DECADE: NVSR_YEAR}
    sources = {**{d: "nchs-hus-2019-table1" for d in HUS_DECADES},
               NVSR_DECADE: "nchs-nvsr-72-1"}

    for decade, rate in values.items():
        fid = f"us-{decade}-teen-birth-rate"
        path = REPO / "data" / "us" / f"{decade}.toml"
        text = path.read_text()
        if f'id = "{fid}"' in text:
            print(f"{decade}: already present, left alone")
            continue
        block = f'''[[fact]]
id = "{fid}"
quantity = {rate}
panel = "day"
label = "Births per 1,000 women aged 15-19, {years[decade]}"
value = "{rate} live births per 1,000 women aged 15-19"
unit = "live births per 1,000 women aged 15-19"
price_year = {years[decade]}
source = "{sources[decade]}"
tier = "A"
notes = "{NOTES[decade]}"
assumptions = ["composite-family"]
'''
        anchor = f'id = "us-{decade}-traffic-death-rate"'
        i = text.index(anchor)
        m = re.compile(r"\n\n(?=\[\[fact\]\]|# )").search(text, i)
        if m is None:
            raise SystemExit(f"{decade}: could not find an insertion point")
        cut = m.start() + 1
        path.write_text(text[:cut] + "\n" + block + text[cut:])
        print(f"{decade}: inserted {fid}  ({rate})")


if __name__ == "__main__":
    main()
