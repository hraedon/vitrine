"""Re-extract two visually checked NFS 1984 food-at-home observations.

Requires the curator-only pypdf package. The report's OCR text layer has a
split quarterly egg numeral and a damaged purchases column. Those readings
are not used: the selected annual consumption cells were independently read
from the page image. Original bytes, row text, units and method are pinned.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILE = "31-uk-expenditure/Domestic_Food_Consumption_and_Expenditure_1984.pdf"
SHA256 = "b462e25868b77ba74e17eabeac4679837d5b0fe4382a977861886bbba04a72b2"


def decimal_token(token: str) -> str:
    if not re.fullmatch(r"\d+-\d+", token):
        raise ValueError("selected cell is not an unambiguous source decimal")
    return str(Decimal(token.replace("-", ".")))


def extract(blob: bytes) -> dict[str, object]:
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError("original NFS report bytes differ from inspected vintage")
    import io

    from pypdf import PdfReader

    logging.getLogger("pypdf").setLevel(logging.ERROR)
    reader = PdfReader(io.BytesIO(blob))
    table = reader.pages[39].extract_text() or ""
    method = re.sub(r"\s+", " ", reader.pages[156].extract_text() or "")
    coverage = re.sub(r"\s+", " ", reader.pages[157].extract_text() or "")
    if "oz per person per week, except where otherwise stated" not in table:
        raise ValueError("table-unit context is missing")
    if "not the amount actually consumed" not in method:
        raise ValueError("the acquisition-versus-ingestion definition is missing")
    if "private households in Great" not in method:
        raise ValueError("the household population is missing")
    if "mainland Great Britain (including the Isle of Wight" not in coverage:
        raise ValueError("the geographical sampling scope is missing")
    milk_rows = [line for line in table.splitlines() if "Liquid wholemilk,full price" in line]
    egg_rows = [line for line in table.splitlines() if line.startswith("EGGS (no)")]
    if len(milk_rows) != 1 or len(egg_rows) != 1:
        raise ValueError("selected food row is missing or ambiguous")
    milk_tokens = milk_rows[0].split("(pt)")[-1].split()
    egg_tokens = egg_rows[0].split("(no)")[-1].split()
    if len(milk_tokens) != 6 or len(egg_tokens) != 7:
        raise ValueError("inspected OCR column layout has changed")
    # Milk has four quarterly columns; the fifth token is annual consumption.
    # Egg's third quarter is split by OCR; annual consumption is penultimate.
    return {
        "source_sha256": SHA256,
        "year": "1984", "table": "8", "printed_page": "28", "pdf_page": "40",
        "column": "Consumption: Yearly average",
        "population": (
            "Private households in mainland Great Britain and Isle of Wight; "
            "excludes Scilly Isles and Scottish islands; one-week food diaries"
        ),
        "definition": "Food entering the household, not amounts actually eaten",
        "milk": {
            "value": decimal_token(milk_tokens[4]), "unit": "pints per person per week",
            "item": "Liquid whole milk, full price", "source_row": milk_rows[0],
        },
        "eggs": {
            "value": decimal_token(egg_tokens[-2]), "unit": "number per person per week",
            "item": "Eggs", "source_row": egg_rows[0],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=REPO / "samples")
    args = parser.parse_args()
    result = extract((args.samples / FILE).read_bytes())
    destination = args.samples / "59-workbook-review" / "nfs-1984-observations.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Re-extracted selected NFS 1984 source cells to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
