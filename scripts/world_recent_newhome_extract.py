"""Check Census new-home median floor areas from the pinned XLS workbook.

Curator artifact only; LiteralBook rejects formula-backed cells. The core does
not depend on xlrd, which is required only for this optional reviewer utility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from workbook_review_extract import LiteralBook

SHA = "81c9156cde3dcfc43e5cc97c827fd83c1f076d5fc621feb6f50ba955c44e5735"
SHEET = "SFTotalMedAvgSqFt"
ROWS = ((26, 1990, 1905), (36, 2000, 2057), (46, 2010, 2169), (60, 2024, 2146))


def extract(path: Path) -> dict[str, object]:
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != SHA:
        raise ValueError("Census workbook changed")
    book = LiteralBook(blob)
    if "New Single-Family Houses Completed" not in str(book.cell(SHEET, 1, 1)):
        raise ValueError("Census table title changed")
    if (book.cell(SHEET, 4, 2), book.cell(SHEET, 6, 2), book.cell(SHEET, 7, 2)) != (
        "Median square feet",
        "United",
        "States",
    ):
        raise ValueError("Census national median heading changed")
    years = {}
    for row, year, value in ROWS:
        if (book.cell(SHEET, row, 1), book.cell(SHEET, row, 2)) != (year, value):
            raise ValueError(f"Census row changed: {year}")
        years[str(year)] = {
            "median_sqft": value,
            "population": "new single-family houses completed",
        }
    return {
        "provenance": "Curator extraction from pinned Census new-house median workbook",
        "years": years,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("workbook", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    args.output.write_text(
        json.dumps(extract(args.workbook), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
