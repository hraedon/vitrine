#!/usr/bin/env python3
"""Extract the Plan 027 WI-2 smoking series from the archived primary tables.

Emits three series TOMLs from the documents under ``samples/34-smoking/``
(never committed; the archive is the transcription source):

- ``data/series/us-cigarettes-per-capita.toml``  — MMWR Surveillance Summary
  Vol. 43 No. SS-3, Table 1: manufactured cigarettes per capita (adults >=18),
  1900-1994, USDA/ERS basis. The HTML preview flattens the table to text rows
  ``year total(billions) per-capita +change``; this script reads the
  per-capita column only. 1993 is provisional and 1994 projected (footnoted
  in the table; carried in the series notes).
- ``data/series/us-cigarettes-per-capita-ttb.toml`` — CDC "Adult Tobacco
  Consumption in the U.S., 2000-Present" CSV, cigarette removals, total
  (domestic + imports) per capita over the 18+ population, 2000-2023. The
  CSV's ``Population`` column is the adult denominator; the per-capita
  columns are precomputed and transcribed as-is. Splices from the USDA
  segment (the basis switch is a methodology splice, not a continuity).
- ``data/series/us-smoking-prevalence.toml`` — CDC/NCHS "Trends in Current
  Cigarette Smoking" table (archived snapshot 2018-11-13), Adults column:
  % of adults >=18 who are current smokers, NHIS survey years 1965-2014.
  Sparse by construction: the NHIS smoked-current question ran in survey
  years only, so absent years are gaps, never zeros. 2015+ omitted (the
  post-2014 figures available to us are Early Release preliminary estimates
  or secondary analysis; extending the series is a later work item).

Spot-verification (see docs/verification-log.md, Plan 027 WI-2): parsed rows
are printed at the end; the operator compares them against the source text.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SMOKING = REPO / "samples" / "34-smoking"
OUT_DIR = REPO / "data" / "series"

MMWR_HTML = SMOKING / "mmwr-tobacco-surveillance-1900-1994.html"
CDC_CSV = SMOKING / "adult-tobacco-consumption-2000-present.csv"
TRENDS_HTML = SMOKING / "cdc-trends-cig-smoking-1965-2014.html"


def mmwr_per_capita() -> dict[int, int]:
    """Table 1 per-capita column, 1900-1994, from the flattened HTML rows."""
    html = MMWR_HTML.read_text()
    start = html.find('<a name="00000792.htm">Table_1</a>')
    end = html.find('<a name=', start + 10)
    text = re.sub(r"<[^>]+>", " ", html[start:end])
    text = re.sub(r"\s+", " ", text)
    values: dict[int, int] = {}
    # row shape: year [footnote marker] total(billions) per-capita [+change].
    # 1900 has no change column; 1993/1994 carry '@'/'&' footnote markers
    # (provisional/projected) between the year and the total.
    for m in re.finditer(
        r"\b(19\d\d)\s*(?:&amp;|[@&])?\s+([\d.]+)\s+([\d,]+)\b", text
    ):
        year, per_capita = int(m.group(1)), int(m.group(3).replace(",", ""))
        if 1900 <= year <= 1994:
            values[year] = per_capita
    if len(values) != 95:
        raise SystemExit(
            f"expected 95 annual rows (1900-1994), parsed {len(values)} — "
            "the MMWR layout changed; inspect before trusting"
        )
    return values


def cdc_csv_per_capita() -> dict[int, int]:
    """Cigarette removals, total per capita (18+ denominator), 2000-2023."""
    values: dict[int, int] = {}
    with CDC_CSV.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if (
                row["Topic"] == "Combustible Tobacco"
                and row["Submeasure"] == "Cigarette Removals"
            ):
                values[int(row["Year"])] = int(row["Total Per Capita"].replace(",", ""))
    if not values or min(values) != 2000:
        raise SystemExit("CDC CSV parse unexpected — inspect before trusting")
    return values


def trends_prevalence() -> dict[int, float]:
    """Adults column (%) of the CDC trends table, 1965-2014 survey years."""
    html = TRENDS_HTML.read_text()
    # blank cells carry '<!-- -->' placeholder comments; strip them first
    html = re.sub(r"<!--.*?-->", "", html)
    # The table rows: <th scope="row">YYYY</th> <td>students</td> <td>adults</td>
    # with blanks for years a column does not report.
    rows = re.findall(
        r"<th[^>]*>\s*(\d{4})\s*</th>\s*<td>\s*([^<]*)</td>\s*<td>\s*([^<]*)</td>",
        html,
    )
    values: dict[int, float] = {}
    for year, _students, adults in rows:
        adults = adults.strip()
        if adults:
            values[int(year)] = float(adults)
    if min(values) != 1965 or max(values) < 2010:
        raise SystemExit(
            f"trends table span unexpected ({min(values)}-{max(values)}) — "
            "the archived snapshot changed; inspect before trusting"
        )
    return values


def emit(
    path: Path,
    series_id: str,
    label: str,
    source: str,
    unit: str,
    population: str,
    notes: str,
    values: dict[int, int | float],
    splices_from: str = "",
) -> None:
    lines = [
        f"# Auto-generated by scripts/mmwr_tobacco_extract.py from {source}",
        "# (samples/34-smoking/ — see the source registry entry and the",
        "# verification log, Plan 027 WI-2, before editing by hand).",
        "",
        "[[series]]",
        f'id = "{series_id}"',
        f'label = "{label}"',
        f'source = "{source}"',
        'tier = "A"',
        f'unit = "{unit}"',
        f'population = "{population}"',
    ]
    if splices_from:
        lines.append(f'splices_from = "{splices_from}"')
    lines.append(f'notes = "{notes}"')
    lines.append("")
    lines.append("[series.values]")
    for year in sorted(values):
        v = values[year]
        v = f"{v:.1f}" if isinstance(v, float) else str(v)
        lines.append(f"{year} = {v}")
    lines.append("")
    path.write_text("\n".join(lines))
    print(f"wrote {path} ({len(values)} values)")


def main() -> None:
    mmwr = mmwr_per_capita()
    ttb = cdc_csv_per_capita()
    prev = trends_prevalence()

    emit(
        OUT_DIR / "us-cigarettes-per-capita.toml",
        "us-cigarettes-per-capita",
        "Cigarette consumption per capita (adults 18+), USDA/ERS 1900-1994",
        "cdc-mmwr-tobacco-surveillance",
        "manufactured cigarettes per adult (18+) per year",
        "U.S. adult population (18+); consumption basis includes overseas military from 1930",
        "MMWR SS-3 Table 1, per-capita column (USDA/ERS from ATF tax data, "
        "imports, Census population). 1993 provisional, 1994 projected "
        "(table footnotes). 1995-1999 have no published value in the "
        "archived record: the gap is the exhibit.",
        mmwr,
    )
    emit(
        OUT_DIR / "us-cigarettes-per-capita-ttb.toml",
        "us-cigarettes-per-capita-ttb",
        "Cigarette consumption per capita (adults 18+), TTB removals 2000-2023",
        "cdc-tobacco-consumption-2000",
        "manufactured cigarettes per adult (18+) per year (taxable removals, domestic + imports)",
        "U.S. adult population (18+), taxable removals basis",
        "CDC dataset from TTB taxable removals over the Census 18+ "
        "population. Splices the USDA/ERS series at a methodology change: "
        "removals are not tax-paid consumption; comparability caveat on "
        "every use.",
        ttb,
        splices_from="us-cigarettes-per-capita",
    )
    emit(
        OUT_DIR / "us-smoking-prevalence.toml",
        "us-smoking-prevalence",
        "Adult cigarette smoking prevalence (NHIS current smokers), 1965-2014",
        "cdc-nhis-smoking-prevalence",
        "% of adults (18+) who are current cigarette smokers",
        "U.S. civilian noninstitutionalized adults 18+ (NHIS household interviews)",
        "CDC/NCHS trends table, Adults column, survey years only (sparse: "
        "absent years are gaps, never zeros). Definition: >=100 lifetime "
        "cigarettes and currently smoking; 'some days' added 1992; "
        "questionnaire redesigned 1997 and again Jan 2019. 2015+ omitted "
        "pending final published values.",
        prev,
    )

    print("\nspot-verification rows (compare against the sources by eye):")
    for year in (1900, 1920, 1940, 1950, 1963, 1964, 1970, 1980, 1990, 1994):
        print(f"  MMWR {year}: {mmwr[year]}")
    for year in (2000, 2010, 2020, 2023):
        print(f"  CSV  {year}: {ttb[year]}")
    for year in (1965, 1970, 1980, 1990, 1993, 1995, 2005, 2010, 2013):
        print(f"  NHIS {year}: {prev.get(year, '(blank cell in table)')}")


if __name__ == "__main__":
    main()
