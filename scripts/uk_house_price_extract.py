#!/usr/bin/env python3
"""Extract UK average house prices, and cross-check the three available series.

Primary (what the rooms cite): ONS House Price Index annual tables,
``samples/32-uk-housing/ons-hpi-annual-tables.xls``, **Table 31 — simple
average house prices, United Kingdom**, unadjusted (nominal), from 1991.

Two other series in the archive measure something adjacent, and are printed
beside it so the reader of the log can see that they disagree and why:

- ONS HPI **Table 28** — the same survey broken down by dwelling type and buyer
  type, from 1986, with the average recorded income of the borrowers beside each
  price. Its *all dwellings* column reproduces Table 31 to the pound, which is
  what makes it a usable control on the Table 31 read.
- **Nationwide** UK house prices since 1952 Q4 — a lender's own mix-adjusted
  index, the only series in the archive reaching back before 1986, and not an
  official statistic. Printed for the pre-1991 decades and as a sanity check,
  never as the cited value where an ONS series exists.

Trap: ``ons-hpi-annual-tables.xlsx`` and ``ons-hpi-data.xlsx`` in the archive
are **HTML landing pages saved with a spreadsheet extension** — openpyxl fails
on them with BadZipFile. The real workbook is the ``.xls``.

Usage: ``python scripts/uk_house_price_extract.py [year ...]``
"""

from __future__ import annotations

import sys
from pathlib import Path

import xlrd

REPO = Path(__file__).resolve().parent.parent
HOUSING = REPO / "samples" / "32-uk-housing"
ONS_HPI = HOUSING / "ons-hpi-annual-tables.xls"
NATIONWIDE = HOUSING / "nationwide-house-prices-1952.xls"

DEFAULT_YEARS = (1970, 1980, 1990, 1997, 2000, 2010)


def ons_table31() -> dict[int, float]:
    """Year -> simple average UK house price, £, unadjusted."""
    sh = xlrd.open_workbook(ONS_HPI).sheet_by_name("Table 31")
    header = " ".join(str(sh.cell_value(r, c)) for r in range(3) for c in range(sh.ncols))
    if "Simple average price" not in header or "Unadjusted" not in header:
        raise SystemExit(f"Table 31 header changed: {header!r}")
    out = {}
    for r in range(sh.nrows):
        year, unadjusted = sh.cell_value(r, 0), sh.cell_value(r, 1)
        if isinstance(year, float) and 1900 < year < 2100 and isinstance(unadjusted, float):
            out[int(year)] = unadjusted
    return out


def ons_table28() -> dict[int, tuple[float, float]]:
    """Year -> (average price, average borrower income) for **all dwellings**, UK.

    Table 28 breaks the same survey down five ways across 25 columns — new
    dwellings, other dwellings, all dwellings, first-time buyers, former owner
    occupiers — each with its own price/advance/income triple. Reading a fixed
    column index picks the *new dwellings* block, which runs well above the
    all-dwellings average and turns this cross-check into a false alarm. The
    block is therefore located by its composed header.
    """
    sh = xlrd.open_workbook(ONS_HPI).sheet_by_name("Table 28")
    headers = {
        c: " ".join(
            str(sh.cell_value(r, c)).strip()
            for r in range(2, 12)
            if str(sh.cell_value(r, c)).strip()
        )
        for c in range(sh.ncols)
    }
    price_col = next(
        (c for c, h in headers.items() if h.startswith("All dwellings") and "price" in h), None
    )
    if price_col is None:
        raise SystemExit(f"Table 28: no 'All dwellings ... price' column in {headers}")
    income_col = next(
        (c for c in sorted(headers) if c > price_col and "income of borrowers" in headers[c]), None
    )
    if income_col is None:
        raise SystemExit("Table 28: no borrower-income column after the all-dwellings price")

    out: dict[int, tuple[float, float]] = {}
    uk_row = next(
        (r for r in range(sh.nrows) if str(sh.cell_value(r, 0)).strip() == "UNITED KINGDOM"), None
    )
    if uk_row is None:
        raise SystemExit("Table 28: no UNITED KINGDOM block")
    for r in range(uk_row, sh.nrows):
        year = sh.cell_value(r, 0)
        if not isinstance(year, float) or not 1900 < year < 2100:
            if out:
                break
            continue
        price, income = sh.cell_value(r, price_col), sh.cell_value(r, income_col)
        if isinstance(price, float) and isinstance(income, float):
            out[int(year)] = (price, income)
    return out


def nationwide_q4() -> dict[int, float]:
    """Year -> Nationwide UK average house price, £, Q4 observation."""
    sh = xlrd.open_workbook(NATIONWIDE).sheet_by_name("UK HP Since 1952")
    out = {}
    for r in range(sh.nrows):
        label, price = str(sh.cell_value(r, 0)).strip(), sh.cell_value(r, 1)
        if label.startswith("Q4 ") and isinstance(price, float):
            out[int(label[3:])] = price
    return out


def main(argv: list[str]) -> int:
    years = [int(a) for a in argv[1:]] or list(DEFAULT_YEARS)
    t31, t28, nw = ons_table31(), ons_table28(), nationwide_q4()
    print(f"ONS Table 31 covers {min(t31)}-{max(t31)}; "
          f"Table 28 {min(t28)}-{max(t28)}; Nationwide Q4 {min(nw)}-{max(nw)}")
    print(f"\n{'year':>6} {'ONS T31 simple avg':>20} {'ONS T28 all dwellings':>22} "
          f"{'T28 borrower income':>21} {'Nationwide Q4':>15}")
    for year in years:
        price28, income28 = t28.get(year, (None, None))
        def fmt(v: float | None) -> str:
            return "—" if v is None else f"£{v:,.0f}"
        print(f"{year:>6} {fmt(t31.get(year)):>20} {fmt(price28):>20} "
              f"{fmt(income28):>21} {fmt(nw.get(year)):>15}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
