"""Replay selected Census histpov2 all-person rates and displayed rounded counts."""

from __future__ import annotations

import hashlib
import json
import tomllib
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PINS = {
    1960: "6f80dc78d317fd2b7ab9690a19b2a411a9aebfdb7d7c37be94b2f935d029618a",
    1970: "69480a06cb839c7dca66951314578f78f40589496436c580899feccfcc76dfc7",
    1980: "c0e484c1add176e5e737ea291811a0e864b85112cf16616b7bdd044ced799fb4",
}
HEADERS = ["NAME", "PCTPOV", "POV", "POP", "PCTFAMPOV", "FAMPOV", "FAM", "YEAR",
           "RACE", "RACE", "time", "us"]


def parse(blob: bytes, year: int) -> tuple[str, str]:
    rows = json.loads(blob)
    if len(rows) != 2 or rows[0] != HEADERS or len(rows[1]) != len(HEADERS):
        raise ValueError("source fields or unique national row changed")
    row = rows[1]
    if row[0] != "United States" or row[7:] != [str(year), "1", "1", str(year), "1"]:
        raise ValueError("source year, all-race or geography selection changed")
    rate, count = Decimal(row[1]), Decimal(row[2])
    if not 0 <= rate <= 100 or count < 0:
        raise ValueError("invalid source rate/count")
    millions = (count / Decimal(1000000)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return row[1], format(millions, "f")


def qualify(samples: Path, data: Path) -> None:
    for year, digest in PINS.items():
        path = samples / f"remaining-audit-20261028/census-poverty-{year}.json"
        blob = path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != digest:
            raise ValueError("inspected Census response bytes changed")
        rate, millions = parse(blob, year)
        facts = tomllib.loads((data / "us" / f"{year}s.toml").read_text(encoding="utf-8"))["fact"]
        fact = next(f for f in facts if f["id"] == f"us-{year}s-poverty-rate")
        if fact["value"] != f"{rate}% ({millions} million people in poverty)":
            raise ValueError("all-person rate/count differs from pinned source")


if __name__ == "__main__":
    qualify(REPO / "samples", REPO / "data")
    print("Reproduced three all-person poverty rates and their rounded counts")
