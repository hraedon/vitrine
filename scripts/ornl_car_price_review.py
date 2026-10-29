"""Reproduce ORNL Edition 39 Table 11.13 current-dollar total car prices.

The output is a curator extraction from a pinned publisher PDF, not publisher
data. pypdf is needed only for this research utility, not the core runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SOURCE_SHA = "f0f041b1b9c844136e10f2d455c3082fe7c3f5f631e4894e9f402c816747b0b1"
YEARS = {1970: 3543, 1980: 7557, 1990: 15033, 2000: 21030, 2010: 24907, 2020: 27366}
TITLE = "Average Price of a New Car (Domestic and Import), 1970–2020"
POPULATION = "Average new car, excluding pickups, vans and sport utility vehicles"


def parse_page(text: str) -> dict[str, object]:
    normalized = " ".join(text.split())
    if "Table 11.13 (Updated April 2021)" not in normalized or TITLE not in normalized:
        raise ValueError("Table number, title or vintage changed")
    header = re.compile(
        r"Domestic[a]?\s+Import\s+Total\s+Year\s+"
        r"Current\s+dollars\s+Constant 2020\s+dollars[b]?\s+"
        r"Current\s+dollars\s+Constant 2020\s+dollars[b]?\s+"
        r"Current\s+dollars\s+Constant 2020\s+dollars[b]?"
    )
    if not header.search(normalized):
        raise ValueError("Domestic/import/total and dollar-column headings changed")
    if "do not include prices for pickups, vans, or sport utility vehicles" not in normalized:
        raise ValueError("Vehicle population note changed")
    if "Bureau of Economic Analysis, Average Transaction Price per New Car" not in normalized:
        raise ValueError("Underlying BEA source changed")
    rows = {}
    for year, expected in YEARS.items():
        matches = re.findall(
            rf"(?m)^\s*{year}\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+"
            r"([\d,]+)\s+([\d,]+)\s+([\d,]+)\s*$",
            text,
        )
        if len(matches) != 1:
            raise ValueError(f"Missing or ambiguous six-column row: {year}")
        numbers = tuple(int(x.replace(",", "")) for x in matches[0])
        if numbers[4] != expected:
            raise ValueError(f"Unexpected total current-dollar value: {year}")
        rows[str(year)] = {"total_current_dollars": numbers[4], "population": POPULATION}
    return {
        "provenance": "Curator extraction from pinned ORNL TEDB Edition 39 Table 11.13",
        "source_sha256": SOURCE_SHA,
        "table": TITLE,
        "column": "Total, current dollars",
        "years": rows,
    }


def extract(path: Path) -> dict[str, object]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("ORNL PDF bytes changed")
    from pypdf import PdfReader

    return parse_page(PdfReader(path).pages[287].extract_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(extract(args.pdf), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
