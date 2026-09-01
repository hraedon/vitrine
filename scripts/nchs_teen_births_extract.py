#!/usr/bin/env python3
"""Extract the Plan 027 WI-5 teen-birthrate series from NCHS.

Emits ``data/series/us-teen-birth-rate.toml`` from *Health, United States,
2019*, Table 1 ("Crude birth rates, fertility rates, and birth rates, by age,
race, and Hispanic origin of mother: United States, selected years
1950-2018"), archived at
``samples/45-teen-births/hus-2019-table1-birth-rates.pdf``. The 2019 edition
is the source rather than the newer 2020-2021 one because the later edition
drops 2010 from its selected years, and 2010 is a decade the museum has a
room for; the later edition serves as a witness instead.

The series is **sparse by construction**: NCHS publishes this table for
selected years, not every year, and the museum renders what is published
rather than interpolating between the printed rows.

**Two traps this parser is built around.**

1. *The wrong race block.* The table repeats its whole year-by-year structure
   once per race and Hispanic-origin group. Reading the first year rows the
   text layer offers can land in a race breakout instead of the All-races
   block — in the companion NVSR report the first such block encountered is
   Hispanic, whose 2020 rate is 23.0 against the all-races 15.0. The parser
   therefore reads only between the "All races" heading and the next race
   heading, and asserts it found that boundary.
2. *The wrong age column.* "15-19 years" is a spanner over three columns —
   Total, 15-17, 18-19 — and 10-14 sits immediately before it. The parser
   takes the fourth numeric cell of a row (crude, fertility, 10-14, then
   15-19 Total) and the cross-checks below would fail loudly on an off-by-one.

**Cross-checks.** Two further NCHS documents are archived beside the source
and compared to it by ``--cross-check``: the later *Health, United States,
2020-2021* Table Brth (a later edition of the same table) and *Births: Final Data
for 2021* (NVSR 72-1) Table 2, which is compiled independently of the trend
tables. Overlap must be non-empty, and every overlapping year must match.

Spot-verification: see docs/verification-log.md, Plan 027 WI-5.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / "samples" / "45-teen-births"
SOURCE = ARCHIVE / "hus-2019-table1-birth-rates.pdf"
WITNESS_HUS_LATER = ARCHIVE / "hus-2020-2021-tableBrth-birth-rates.pdf"
WITNESS_NVSR = ARCHIVE / "nvsr72-01-births-final-2021.pdf"
OUT = REPO / "data" / "series" / "us-teen-birth-rate.toml"

YEAR = re.compile(r"(19|20)\d{2}[\s.]*")
CELL = re.compile(r"[\d,]+\.\d")
ALL_RACES = ("All races",)
RACE_BREAKOUT = ("Race of child", "Non-Hispanic", "Hispanic")

# Which numeric cell of a row is the 15-19 "Total" column depends on the
# document's own column set, so it is stated per document rather than assumed:
#   HUS trend tables : crude birth rate, fertility rate, 10-14, 15-19 Total
#   NVSR Table 2     : total fertility rate, 10-14, 15-19 Total
# Getting this wrong reads the 15-17 sub-column instead, which is roughly half
# the value and entirely plausible on its own. That is what the cross-check is
# for: an off-by-one here makes the two documents disagree, loudly.
COL_HUS = 3
COL_NVSR = 2


def _lines(pdf: Path, must_contain: str = "") -> list[str]:
    """Lines of the document, or only of pages carrying ``must_contain``.

    The page filter is not cosmetic. A report can repeat an "All races"
    heading on several pages for several different tables, and concatenating
    the document would make the block finder latch onto the first one it sees
    — a different table with different columns. Naming the table is how the
    caller says which one it means.
    """
    import fitz

    pages = [page.get_text() for page in fitz.open(pdf)]
    if must_contain:
        pages = [t for t in pages if must_contain in t]
        if not pages:
            raise SystemExit(f"{pdf.name}: no page contains {must_contain!r}")
    return [line.strip() for t in pages for line in t.splitlines() if line.strip()]


def _all_races_block(lines: list[str]) -> list[str]:
    start = next(
        (i for i, line in enumerate(lines) if line.startswith(ALL_RACES)), None
    )
    if start is None:
        raise SystemExit("no 'All races' heading — cannot tell which block is which")
    stop = next(
        (i for i, line in enumerate(lines[start + 1 :], start + 1)
         if line.startswith(RACE_BREAKOUT)),
        len(lines),
    )
    if stop == len(lines):
        raise SystemExit(
            "no race-breakout heading after 'All races' — the block boundary is "
            "unproven and the parse could be reading a breakout's rows"
        )
    return lines[start:stop]


def parse(pdf: Path, must_contain: str = "", column: int = COL_HUS) -> dict[int, float]:
    block = _all_races_block(_lines(pdf, must_contain))
    out: dict[int, float] = {}
    i = 0
    while i < len(block):
        if not YEAR.fullmatch(block[i]):
            i += 1
            continue
        cells, j = [], i + 1
        while j < len(block) and CELL.fullmatch(block[j]):
            cells.append(float(block[j].replace(",", "")))
            j += 1
        if len(cells) > column:
            out[int(block[i][:4])] = cells[column]
        i = max(j, i + 1)
    if not out:
        raise SystemExit(f"{pdf.name}: parsed no rows")
    return out


def cross_check(rates: dict[int, float]) -> None:
    witnesses = (
        ("HUS 2020-2021 Table Brth", WITNESS_HUS_LATER, "", COL_HUS),
        ("NVSR 72-1 Table 2", WITNESS_NVSR,
         "Table 2. Birth rates, by age of mother", COL_NVSR),
    )
    for name, pdf, marker, column in witnesses:
        witness = parse(pdf, marker, column)
        common = sorted(set(rates) & set(witness))
        if len(common) < 5:
            raise SystemExit(
                f"{name}: only {len(common)} overlapping years — the cross-check "
                "would be vacuous, so it is treated as a failure"
            )
        bad = {y: (rates[y], witness[y]) for y in common if rates[y] != witness[y]}
        if bad:
            raise SystemExit(f"{name} disagrees on {bad}")
        print(f"  {name}: {len(common)} overlapping years, all identical")


def render_toml(rates: dict[int, float]) -> str:
    lines = [
        "# Auto-generated by scripts/nchs_teen_births_extract.py from Health,",
        "# United States 2019, Table 1 (samples/45-teen-births/ — see the",
        "# source registry entry and the verification log, Plan 027 WI-5, before",
        "# editing by hand).",
        "",
        "[[series]]",
        'id = "us-teen-birth-rate"',
        'label = "Births per 1,000 women aged 15-19, selected years 1950-2018"',
        'source = "nchs-hus-2019-table1"',
        'tier = "A"',
        'unit = "live births per 1,000 women aged 15-19"',
        'population = "All women aged 15-19 in the United States, all races and origins — '
        'a rate over every woman in the age band, not over those who were sexually active"',
        'notes = "Table Brth, All-races block, the 15-19 \'Total\' column (the table also '
        "prints 15-17 and 18-19 sub-columns beside it). Sparse by construction: NCHS "
        "publishes selected years, not every year, and the gaps between printed rows are "
        "not interpolated. The series starts at 1950 because that is where the published "
        'table starts."',
        "",
        "[series.values]",
    ]
    for year in sorted(rates):
        lines.append(f"{year} = {rates[year]}")
    return "\n".join(lines) + "\n"


def main() -> None:
    rates = parse(SOURCE)
    print(f"parsed {len(rates)} years from {SOURCE.name}: "
          f"{min(rates)}-{max(rates)}")
    print("cross-checks:")
    cross_check(rates)

    OUT.write_text(render_toml(rates))
    print(f"\nwrote {OUT.relative_to(REPO)}")
    print()
    print("== the published rows ==")
    for year in sorted(rates):
        print(f"  {year}  {rates[year]}")
    peak = max(rates, key=lambda y: rates[y])
    print()
    print("== the shape ==")
    print(f"  highest published row: {peak} at {rates[peak]}")
    rises = [y for a, y in zip(sorted(rates), sorted(rates)[1:], strict=False)
             if rates[y] > rates[a]]
    print(f"  years that rose on the previous published row: {rises}")


if __name__ == "__main__":
    main()
