"""Stream selected household-sector balance sheets from the original Fed CSV ZIP.

The publisher repeats metadata on every historical row; the uncompressed file
is large. Filter physical rows by an exact series prefix, parse selected rows
strictly, and never unpack the whole dataset or publish its underlying tables.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

FILE = "remaining-audit-20261028/FRB_Z1_csv-20261028.zip"
SHA256 = "83b8eded0bc7f9b74c0269ef503a863cee88312460fd7eef076284b98fc28c06"
SERIES = ("FL152090005.Q", "FL152000005.Q", "FL154190005.Q")
HEADERS = ["series_name", "short_description", "long_description", "currency", "frequency",
           "series_instrument", "series_prefix", "series_sector", "series_type", "unit",
           "unit_mult", "date", "value"]


def parse_selected(line: bytes) -> dict[str, str]:
    rows = list(csv.reader([line.decode("utf-8")], strict=True))
    if len(rows) != 1 or len(rows[0]) != len(HEADERS):
        raise ValueError("selected source row is not a complete CSV record")
    row = dict(zip(HEADERS, rows[0], strict=True))
    if (row["currency"] != "United States / United States Dollar"
            or row["frequency"] != "Quarterly" or row["unit"] != "Currency"
            or row["unit_mult"] != "Millions"
            or "Households and nonprofit organizations" not in row["short_description"]):
        raise ValueError("source population, units or frequency changed")
    if not row["value"].isdigit():
        raise ValueError("selected balance sheet value is missing or not literal")
    return row


def extract(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != SHA256:
            raise ValueError("inspected Federal Reserve archive bytes changed")
    prefixes = tuple(f"Z1/Z1/{code},".encode() for code in SERIES)
    observations: dict[str, dict[str, dict[str, str]]] = {}
    with ZipFile(path) as archive, archive.open("Z1.csv") as source:
        header = next(csv.reader([source.readline().decode("utf-8-sig")]))
        if header != HEADERS:
            raise ValueError("Federal Reserve CSV structure changed")
        for line in source:
            if not line.startswith(prefixes):
                continue
            row = parse_selected(line)
            if row["date"] not in {"1950-12-31", "1960-12-31", "1970-12-31"}:
                continue
            code = row["series_name"].removeprefix("Z1/Z1/")
            selected = observations.setdefault(row["date"][:4], {})
            if code in selected:
                raise ValueError("duplicate selected quarter/series")
            selected[code] = row
    for year in ("1950", "1960", "1970"):
        selected = observations.get(year, {})
        if set(selected) != set(SERIES):
            raise ValueError(f"missing source balance sheet: {year}")
        net, assets, liabilities = (int(selected[code]["value"]) for code in SERIES)
        if assets - liabilities != net:
            raise ValueError("published balance sheet identity does not hold")
    return {"source_sha256": SHA256, "unit": "millions of US dollars", "period": "Q4",
            "population": "Households and nonprofit organizations", "observations": observations}


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    result = extract(root / "samples" / FILE)
    destination = root / "samples/remaining-audit-20261028/z1-full-selected.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Selected original Fed net worth, USD millions:",
          {year: rows[SERIES[0]]["value"] for year, rows in result["observations"].items()})
