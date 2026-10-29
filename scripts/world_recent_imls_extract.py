"""Sum FY2020 IMLS state summaries for the 50 states and DC.

This is a curator-produced aggregate, not an IMLS-published national total.
The input contains imputed state totals; the flags are retained in the result.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

SHA = "30da545b230ceec6d29bf8598bfadc8149673ba1f77e8e6787caff9b58c43a79"
STATES = frozenset(
    [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "DC",
    ]
)


def extract(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError("IMLS archive changed")
    with (
        zipfile.ZipFile(io.BytesIO(data)) as archive,
        archive.open("PLS_FY20_State_pud20i.csv") as raw,
    ):
        rows = list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")))
    if len(rows) != 55:
        raise ValueError("Unexpected IMLS row count")
    selected = [row for row in rows if row["STABR"] in STATES]
    if len(selected) != 51 or {row["STABR"] for row in selected} != STATES:
        raise ValueError("Expected each state and DC exactly once")
    if any(
        row["F_REFER"] not in {"R_20", "IF20", "IA20"} or row["REFERENC"] in {"", "-1"}
        for row in selected
    ):
        raise ValueError("Missing or suppressed state total")
    flags = dict(sorted(collections.Counter(row["F_REFER"] for row in selected).items()))
    total = sum(int(row["REFERENC"]) for row in selected)
    if flags != {"IA20": 1, "IF20": 42, "R_20": 8} or total != 139263801:
        raise ValueError("Unexpected imputation flags or total")
    return {
        "provenance": "Curator sum of pinned IMLS FY2020 state summaries",
        "population": "50 states and District of Columbia",
        "flags": flags,
        "reference_transactions": total,
        "million": 1000000,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(extract(args.archive), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
