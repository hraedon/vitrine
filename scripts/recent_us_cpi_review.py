"""Replay Census/BLS inputs to the recent U.S. CPI and real-income facts.

Reads sanitized BLS API responses and Census CPS ASEC Table F-8, verifies
source digests and table context, and writes only to ignored samples/.
"""

from __future__ import annotations

import hashlib
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "samples/remaining-audit-20261028"
F08 = ROOT / "samples/06-acs-csv/f08ar.xlsx"
OUTPUT = SAMPLES / "recent_us-cpi-review.json"
PINS = {
    SAMPLES / "bls-cpi-annual-1990-1999.json": (
        "2909c00308be5b0fa553f1776ec47b86d0bd1a7f9a453d75743cf0acf86a9950"
    ),
    SAMPLES / "bls-cpi-annual-2000-2009.json": (
        "90deeae8c8e677f14001fa7c575caa06d039448deaf6f98d02a4d61c47e6ba4c"
    ),
    SAMPLES / "bls-cpi-annual-2010-2019.json": (
        "f995c5ff3a78aab2a4afad1b7eae012d5232e53f212e1c5123b750731e36da63"
    ),
    SAMPLES / "bls-cpi-annual-2020-2024.json": (
        "621716306a478483b3d38e41ad594284a123892601717153cc3401ec1d8c8a72"
    ),
    F08: "2eb2802f80d6e46d7e76f6f133cc1b50fa5ae2342b6918e22459d1b9c67b6cf8",
}
YEARS = (1990, 2000, 2010, 2024)


def check_hash(path: Path, expected: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"source digest mismatch: {path.name}")


def read_cpi() -> dict[int, Decimal]:
    values: dict[int, Decimal] = {}
    for path in sorted(p for p in PINS if p.name.startswith("bls-cpi-annual-")):
        check_hash(path, PINS[path])
        response = json.loads(path.read_text(encoding="utf-8"))
        if response.get("status") != "REQUEST_SUCCEEDED":
            raise ValueError(f"BLS API response not successful: {path.name}")
        series = response.get("Results", {}).get("series", [])
        if len(series) != 1 or series[0].get("seriesID") != "CUUR0000SA0":
            raise ValueError(f"unexpected BLS CPI series context: {path.name}")
        for obs in series[0].get("data", []):
            if obs.get("period") != "M13":
                continue
            year = int(obs["year"])
            values[year] = Decimal(obs["value"])
    for year in YEARS:
        if year not in values:
            raise ValueError(f"missing official annual average for {year}")
    return values


def read_f8() -> dict[int, int]:
    check_hash(F08, PINS[F08])
    workbook = load_workbook(F08, data_only=True, read_only=True)
    sheet = workbook["f08ar"]
    start = next(
        (r for r in range(1, sheet.max_row + 1) if sheet.cell(r, 1).value == "All Families"),
        None,
    )
    if start is None:
        raise ValueError("Census F-8 All Families context missing")
    incomes: dict[int, int] = {}
    for row in range(start + 3, sheet.max_row + 1):
        label = sheet.cell(row, 1).value
        if isinstance(label, int):
            year = label
        elif isinstance(label, str):
            import re

            match = re.match(r"^(\d{4})", label.strip())
            if match is None:
                if label.strip():
                    break
                continue
            year = int(match.group(1))
        else:
            if label is not None:
                break
            continue
        value = sheet.cell(row, 3).value
        if isinstance(value, int | float) and not isinstance(value, bool):
            incomes.setdefault(year, int(value))
    workbook.close()
    if any(year not in incomes for year in YEARS):
        raise ValueError("Census F-8 is missing an All Families year")
    return incomes


def two_places(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def main() -> None:
    cpi = read_cpi()
    income = read_f8()
    results: dict[str, Any] = {}
    for year in (1990, 2000, 2010):
        cpi_ratio = cpi[2024] / cpi[year]
        income_ratio = Decimal(income[2024]) / Decimal(income[year])
        real_ratio = income_ratio / cpi_ratio
        results[str(year)] = {
            "cpi_year": str(cpi[year]),
            "cpi_2024": str(cpi[2024]),
            "cpi_ratio_2024_over_year": two_places(cpi_ratio),
            "all_families_income_year": income[year],
            "all_families_income_2024": income[2024],
            "nominal_income_ratio": two_places(income_ratio),
            "real_income_ratio_using_cpi_u": two_places(real_ratio),
        }
    results["2024"] = {
        "cpi": str(cpi[2024]),
        "display_one_decimal": str(cpi[2024].quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
    }
    OUTPUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    for year in (1990, 2000, 2010):
        row = results[str(year)]
        print(
            f"{year}: CPI ratio {row['cpi_ratio_2024_over_year']}; "
            f"real income ratio {row['real_income_ratio_using_cpi_u']}"
        )
    print(
        f"2024 CPI-U annual average: {results['2024']['cpi']} -> "
        f"{results['2024']['display_one_decimal']}"
    )


if __name__ == "__main__":
    main()
