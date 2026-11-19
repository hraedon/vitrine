"""Pin a visual transcription of BLS Table 6, 1950 worker-family housing.

The PDF text layer misreads several cells. Values below were read from the
page image; this is a curator artifact, not machine extraction of numeric cells.
The original PDF hash and page-text sentinels fail closed on source changes.
Research utility only: pypdf is not a core dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = "ba688e0a6130a872b33b1ecb89b304fafe307cca915b397fd4372e24d451219f"
SOURCE_FILE = "reconstruction-20261029/bls/american-buying-habits-1959.pdf"
TABLE = "Table 6, printed p. 46 / PDF p. 60, all income classes"
POPULATION = "Urban wage-earner and clerical-worker families of two or more persons"
DENOMINATOR = "Mean expenditures for current consumption"
HOUSING_SCOPE = (
    "Housing; fuel, light, refrigeration, household operation, and furnishings are separate"
)
SENTINELS = ("6.-C", ";_ oo,", "s:1", "JO.(;", "refrigera1ion")


def review(pdf: Path) -> dict[str, object]:
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("BLS source PDF hash changed")
    from pypdf import PdfReader

    page = PdfReader(pdf).pages[59].extract_text()
    if not all(s in page for s in SENTINELS):
        raise ValueError("BLS page OCR or table location changed; inspect original image")
    return {
        "provenance": (
            "Curator visual transcription from pinned BLS PDF; numeric text layer is unreliable"
        ),
        "source_file": SOURCE_FILE,
        "source_sha256": SOURCE_SHA256,
        "table": TABLE,
        "population": POPULATION,
        "denominator": DENOMINATOR,
        "housing_scope": HOUSING_SCOPE,
        "sample_families": 7007,
        "consumption_dollars": 3925,
        "housing_dollars": 415,
        "housing_percent": 10.6,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(review(args.pdf), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
