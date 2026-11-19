"""Reproduce selected estimates from pinned EIA data and Census API snapshots.

Output is a curator artifact, not publisher-provided data. ACS snapshots contain
only public query responses and metadata, never the API key. Shares use decimal
half-up rounding once, after summing source counts or survey weights.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

PINS = {
    "10-recs/file2_asc.txt": "8f65084d47faa71e92524c33d25a928e3aefbf51f356f709c2c4e69bf8f1f87e",
    "10-recs/file2_cbd.txt": "18d062e9ca3056079d7579a3819fe349ce52929650bf8cb2a731569450d10f45",
    "remaining-audit-20261028/world-recent-originals/acs2024-B25003.json":
        "8bc581c43c8f78bf954420331747141dc32639ff151b90a239fe8af6e7e7bfdb",
    "remaining-audit-20261028/world-recent-originals/acs2024-B25040.json":
        "627d0999586df3043b299861c2520737dd3b2c21e56a524abf3ff205a021f228",
    "remaining-audit-20261028/world-recent-originals/acs2024-B25045.json":
        "e83645406f1d0a9070c37e8b6ad6f0e96689c2b13868a82fa16abfefc54c6f83",
}


def percent(n: int, d: int, places: str) -> str:
    return str((Decimal(n) * 100 / Decimal(d)).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def extract(root: Path) -> dict[str, object]:
    raw = {}
    for path, pin in PINS.items():
        blob = (root / path).read_bytes()
        if hashlib.sha256(blob).hexdigest() != pin:
            raise ValueError(f"Source changed: {path}")
        raw[path] = blob
    records = list(csv.DictReader(raw["10-recs/file2_asc.txt"].decode("ascii").splitlines()))
    totals: dict[str, int] = {}
    for row in records:
        code = row["FUELHEAT"].strip()
        totals[code] = totals.get(code, 0) + int(row["NWEIGHT"])
    if (
        len(records) != 7111
        or sum(totals.values()) != 96631492
        or set(totals) != {"0", "1", "2", "3", "4", "5", "6", "7", "21"}
    ):
        raise ValueError("Unexpected RECS population or categories")
    acs = {}
    for table in ("B25003", "B25040", "B25045"):
        path = f"remaining-audit-20261028/world-recent-originals/acs2024-{table}.json"
        snap = json.loads(raw[path])
        if (
            snap["dataset"] != "2024/acs/acs1"
            or snap["geography"] != "us:1"
            or snap["table"] != table
        ):
            raise ValueError("Unexpected ACS survey or population")
        acs[table] = dict(zip(*snap["response"], strict=True))
    tenure, fuel, vehicle = (acs[t] for t in ("B25003", "B25040", "B25045"))
    total = int(tenure["B25003_001E"])
    if (
        total != 132737146
        or int(fuel["B25040_001E"]) != total
        or int(vehicle["B25045_001E"]) != total
    ):
        raise ValueError("Unexpected ACS total")
    utility = int(fuel["B25040_002E"])
    electricity = int(fuel["B25040_004E"])
    no_vehicle = int(vehicle["B25045_003E"]) + int(vehicle["B25045_012E"])
    return {
        "provenance": ("Curator extraction from pinned EIA microdata and 2024 Census ACS "
                       "1-year API response snapshots; not publisher artifact."),
        "rounding": "decimal half-up, once after aggregation",
        "recs1993": {
            "records": len(records),
            "weighted_total": sum(totals.values()),
            "weighted_by_fuelheat_code": totals,
            "percent_by_fuelheat_code": {k: percent(v, 96631492, "0.1") for k, v in totals.items()},
        },
        "acs2024": {
            "occupied_total": total,
            "owner_count": int(tenure["B25003_002E"]),
            "utility_gas_count": utility,
            "electricity_count": electricity,
            "one_or_more_vehicle_count": total - no_vehicle,
            "owner_percent": percent(int(tenure["B25003_002E"]), total, "0.1"),
            "utility_gas_percent": percent(utility, total, "1"),
            "electricity_percent": percent(electricity, total, "1"),
            "other_or_none_percent": percent(total - utility - electricity, total, "1"),
            "no_vehicle_count": no_vehicle,
            "one_or_more_vehicle_percent": percent(total - no_vehicle, total, "0.1"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("samples", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(extract(args.samples), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
