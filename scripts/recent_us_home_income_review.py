"""Replay recent U.S. home-value / family-income comparisons from pinned inputs.

This review helper reads the Census historical median-home-value table,
ACS 2010 B25077, and Census Table F-8 (All Families). It checks source bytes,
guards the table labels, and reports nominal home-value / annual-family-income
ratios rounded to cents using decimal half-up rounding. It does not edit data/.
"""

from __future__ import annotations

import csv
import hashlib
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from openpyxl import load_workbook

REPO = Path(__file__).resolve().parent.parent
HOME_VALUES = REPO / "samples/05-census-housing/values-unadj.txt"
F08 = REPO / "samples/06-acs-csv/f08ar.xlsx"
ACS_2010 = REPO / "samples/06-acs-csv/ACSDT1Y2010.B25077-2026-07-07T023001.csv"
PINS = {
    HOME_VALUES: "5fbabee6743983f4f39b61c6e42cc9a5727c2266173344ec3fc0381b06a221b6",
    F08: "2eb2802f80d6e46d7e76f6f133cc1b50fa5ae2342b6918e22459d1b9c67b6cf8",
    ACS_2010: "20d49b96e25a9ff1d1d443fa7d0a8d84419d2920d69ced48fa966c9374dc4ec7",
}
EXPECTED = {
    1980: Decimal("2.25"),
    1990: Decimal("2.24"),
    2000: Decimal("2.36"),
    2010: Decimal("2.99"),
}


def check_pins() -> None:
    for path, expected in PINS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"source bytes changed: {path.name}")


def historical_home_values() -> dict[int, int]:
    lines = HOME_VALUES.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "Median Home Values: Unadjusted":
        raise ValueError("unexpected Census historical home-value table title")
    header_index = next(
        (i for i, line in enumerate(lines) if re.search(r"\b2000\s+1990\s+1980\b", line)),
        None,
    )
    if header_index is None:
        raise ValueError("historical home-value year header missing")
    header = re.findall(r"\b(?:19|20)\d{2}\b", lines[header_index])
    row = next(
        (line for line in lines[header_index + 1 :] if line.startswith("United States")), None
    )
    if row is None:
        raise ValueError("United States home-value row missing")
    values = [int(value.replace(",", "")) for value in re.findall(r"\$([\d,]+)", row)]
    if len(header) != len(values):
        raise ValueError("historical home-value header and row lengths disagree")
    return {int(year): value for year, value in zip(header, values, strict=True)}


def f08_all_families_income() -> dict[int, int]:
    workbook = load_workbook(F08, data_only=True, read_only=True)
    sheet = workbook["f08ar"]
    start = next(
        (
            row
            for row in range(1, sheet.max_row + 1)
            if sheet.cell(row=row, column=1).value == "All Families"
        ),
        None,
    )
    if start is None:
        raise ValueError("Census F-8 All Families section missing")
    result: dict[int, int] = {}
    for row in range(start + 3, sheet.max_row + 1):
        raw_year = sheet.cell(row=row, column=1).value
        if isinstance(raw_year, int):
            year = raw_year
        elif isinstance(raw_year, str):
            match = re.match(r"^(\d{4})", raw_year.strip())
            if match is None:
                if raw_year.strip():
                    break
                continue
            year = int(match.group(1))
        else:
            if raw_year is not None:
                break
            continue
        income = sheet.cell(row=row, column=3).value
        if not isinstance(income, int | float) or isinstance(income, bool):
            continue
        result.setdefault(year, int(income))
    workbook.close()
    return result


def acs_2010_home_value() -> int:
    with ACS_2010.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1 or rows[0].get("Label (Grouping)") != "Median value (dollars)":
        raise ValueError("ACS B25077 2010 national row changed")
    return int(rows[0]["United States!!Estimate"].replace(",", ""))


def main() -> int:
    check_pins()
    home = historical_home_values()
    income = f08_all_families_income()
    home[2010] = acs_2010_home_value()
    for year, expected in EXPECTED.items():
        ratio = (Decimal(home[year]) / Decimal(income[year])).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if ratio != expected:
            raise ValueError(f"{year} ratio changed: expected {expected}, got {ratio}")
        print(f"{year}: ${home[year]:,} / ${income[year]:,} = {ratio}")
    print(
        "Sources: Census historical home values, ACS B25077, and CPS ASEC Table F-8 All Families."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
