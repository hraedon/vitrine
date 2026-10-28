"""Qualify compound food-price placards from saved BLS API response bytes.

The public requests used no registration key or contact address. These are
newly retrieved 2026-10-28 vintages, not recreated historical downloads.
FRED's BLS-sourced series pages independently supply item identities/units;
the numerical observations come from BLS. This does not add field-audit
coverage: each placard contains several values and has no single quantity.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import tomllib
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SERIES = (
    ("APU0000702111", "Bread", "lb", "Bread, White, Pan"),
    ("APU0000703111", "ground chuck", "lb", "Ground Chuck, 100% Beef"),
    ("APU0000704111", "bacon", "lb", "Bacon, Sliced"),
    ("APU0000708111", "eggs", "doz", "Eggs, Grade A, Large"),
    ("APU0000712211", "lettuce", "lb", "Lettuce, Iceberg"),
    ("APU0000711211", "bananas", "lb", "Bananas"),
)
RESPONSE_PINS = {
    1980: "39f40dacbbceebc458e97f7a7abd4a7e3ee470977b5cf027a48ea267956843bd",
    1990: "02876afedcf7c330ee0cc32ed85e11d41391a7f43ded3009fe3221cee5f4672a",
    2000: "b9d5a07a3ea0fe79d4a9b83851300da1110dec6180af115f6916cf753c80d114",
    2010: "1363249ec6c6243e5302c9397e2dfc53c9879fe130e4755f919c4cfcfb5a287c",
    2024: "fbe61a9c3b0d043a19690118423d65fce3a23b86ac9f4e4e2964d41e2a6622c6",
}
METADATA_PINS = {
    "APU0000702111": "692c5d5ba392e59c80b91947f0fa52d45bbbf929a145420ec8c7673894abb9cd",
    "APU0000703111": "eee14cba2324156eb0e278660e24ee197f2c670b294caa9b93c0acb4e5479efa",
    "APU0000704111": "57f9eca46b6b09b9a1248725416603968c776ee921c783a75a90d91a4fa09880",
    "APU0000708111": "c4e32cceb6ec5208efe6872e01ab06689b6ec3d3b1dc64a2c567b3a849f4009c",
    "APU0000712211": "5f8f609349dc64064df358d5ed0e01389d06b8866c8d718f086a005632960a8c",
    "APU0000711211": "ece86f8262ee7b7305983741c9e0ddbe07351e7de5602c8a88b164b3d355ab33",
}


def metadata_title(blob: bytes) -> str:
    match = re.search(r"<title>(.*?)</title>", blob.decode("utf-8"), re.I | re.S)
    if match is None:
        raise ValueError("series metadata has no title")
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()


def render(document: dict[str, object], year: int, metadata: dict[str, str]) -> str:
    if document.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError("BLS response did not succeed")
    observations = document["Results"]["series"]
    expected = SERIES if year == 2024 else SERIES[:-1]
    identifiers = [item["seriesID"] for item in observations]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) != {s[0] for s in expected}:
        raise ValueError("unexpected, duplicate or missing food-price series")
    by_id = {item["seriesID"]: item for item in observations}
    parts: list[str] = []
    for identifier, label, unit, description in expected:
        title = metadata[identifier]
        basis = "Cost per Dozen" if unit == "doz" else "Cost per Pound/453.6 Grams"
        expected_title = (
            f"Average Price: {description} ({basis}) in U.S. City Average ({identifier})"
        )
        if expected_title not in title:
            raise ValueError(f"food identity or unit disagrees with series metadata: {identifier}")
        rows = by_id[identifier]["data"]
        selected = [row for row in rows if row["period"] == "M12"]
        if len(selected) != 1:
            raise ValueError("expected exactly one December observation")
        row = selected[0]
        if row["year"] != str(year) or row["periodName"] != "December":
            raise ValueError("December year or period label disagrees")
        if not re.fullmatch(r"\d+(?:\.\d+)?", row["value"]):
            raise ValueError("source price is not an unambiguous nonnegative decimal")
        value = Decimal(row["value"]).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        parts.append(f"{label} ${value:.2f}/{unit}")
    return ", ".join(parts)


def qualify(archive: Path, data: Path) -> None:
    metadata: dict[str, str] = {}
    for identifier, expected in METADATA_PINS.items():
        blob = (archive / f"{identifier}-fred-metadata.html").read_bytes()
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError("inspected metadata bytes changed")
        metadata[identifier] = metadata_title(blob)
    for year, expected in RESPONSE_PINS.items():
        blob = (archive / f"bls-average-prices-{year}-response.json").read_bytes()
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError("inspected BLS response bytes changed")
        decade = "2020s" if year == 2024 else f"{year}s"
        room = tomllib.loads((data / "us" / f"{decade}.toml").read_text(encoding="utf-8"))
        fact = next(f for f in room["fact"] if f["id"] == f"us-{decade}-food-prices")
        if fact["value"] != render(json.loads(blob), year, metadata):
            raise ValueError(f"food-price placard disagrees with original response: {year}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=REPO / "samples/59-workbook-review")
    parser.add_argument("--data", type=Path, default=REPO / "data")
    args = parser.parse_args()
    qualify(args.archive, args.data)
    print("Qualified five compound placards (26 prices); no single-field audit coverage added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
