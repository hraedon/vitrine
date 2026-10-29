"""Compute aggregate 1949 family-income estimates from an authorized IPUMS extract.

This curator tool reads a 1950 1% *rectangular person-record CSV* and its DDI.
It writes only national aggregate results. Individual records and identifiers
must stay in the ignored samples archive; never print or publish them.

IPUMS documents FTOTINC for sample-line household heads in 1950, and requires
SLWT for such observations. The 1950 census income reference year is 1949.
The output distinguishes identifiable outside-central-city households from
metropolitan households whose central-city status is indeterminable.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import NamedTuple

REQUIRED = frozenset(
    {
        "YEAR",
        "SAMPLE",
        "SERIAL",
        "PERNUM",
        "GQ",
        "FAMUNIT",
        "FAMSIZE",
        "RELATE",
        "METRO",
        "FTOTINC",
        "SLWT",
    }
)
METRO_CODES = {
    1: "Not in metropolitan area",
    2: "Metropolitan status indeterminable (mixed)",
    3: "In metropolitan area: Not in central/principal city",
    4: "In metropolitan area: Central/principal city status indeterminable (mixed)",
    5: "In metropolitan area: In central/principal city",
}
GQ_CODES = {1: "Households under 1970 definition"}
HEAD_LABEL = "Head/Householder"
SAMPLE_CODE = 195001
MISSING_INCOME = {9999998, 9999999}
TOP_CODE = 10000
MINIMUM_CELL = 30
DOC_PINS = {
    "ftotinc": "3b4ca7579d01a932eae4addb29ee98ddec65a005e66cdadde90a4ada6861660e",
    "slwt": "909c576740194da1bfe7b358cdab1b3493b7156c27e9848af570720e120f9699",
}
DOCS = {
    "ftotinc": "https://usa.ipums.org/usa-action/variables/FTOTINC",
    "slwt": "https://usa.ipums.org/usa-action/variables/SLWT",
    "metro": "https://usa.ipums.org/usa-action/variables/METRO",
    "famsize": "https://usa.ipums.org/usa-action/variables/FAMSIZE",
    "famunit": "https://usa.ipums.org/usa-action/variables/FAMUNIT",
    "gq": "https://usa.ipums.org/usa-action/variables/GQ",
    "relate": "https://usa.ipums.org/usa-action/variables/RELATE",
}


class ReviewError(ValueError):
    """A source or record invariant failed; messages never disclose records."""


class Observation(NamedTuple):
    income: int
    weight: Decimal


def _tag(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def _categories(var: ET.Element) -> dict[int, str]:
    result: dict[int, str] = {}
    for category in var:
        if _tag(category) != "catgry":
            continue
        parts = {_tag(item): (item.text or "").strip() for item in category}
        raw = parts.get("catValu", "")
        if re.fullmatch(r"[+-]?\d+", raw):
            code = int(raw)
            if code in result:
                raise ReviewError("duplicate DDI category")
            result[code] = " ".join(parts.get("labl", "").split())
    return result


def validate_ddi(blob: bytes) -> dict[str, object]:
    """Require the actual extract DDI, its sample and the relevant code meanings."""
    try:
        root = ET.fromstring(blob)
    except ET.ParseError as exc:
        raise ReviewError("invalid extract DDI") from exc
    variables = [n for n in root.iter() if _tag(n) == "var"]
    names = [n.get("name", "") for n in variables]
    if len(names) != len(set(names)) or not REQUIRED.issubset(names):
        raise ReviewError("DDI lacks required unique variables")
    by_name = {n.get("name", ""): n for n in variables}
    if by_name["SLWT"].get("dcml") != "2":
        raise ReviewError("DDI sample-line weight decimal metadata changed")
    if _categories(by_name["SAMPLE"]).get(SAMPLE_CODE) != "1950 1%":
        raise ReviewError("DDI sample code is not the 1950 1% sample")
    if any(_categories(by_name["METRO"]).get(k) != v for k, v in METRO_CODES.items()):
        raise ReviewError("DDI metropolitan category meanings changed")
    if any(_categories(by_name["GQ"]).get(k) != v for k, v in GQ_CODES.items()):
        raise ReviewError("DDI household category meanings changed")
    if _categories(by_name["RELATE"]).get(1) != HEAD_LABEL:
        raise ReviewError("DDI relationship-to-head category changed")
    # Continuous income variables normally describe special codes in codInstr,
    # rather than DDI catgry elements (as in the inspected INCTOT extract).
    instructions = " ".join(" ".join(by_name["FTOTINC"].itertext()).split())
    for pattern in (
        r"-0*1\s*=\s*Net loss",
        r"0+\s*=\s*No income",
        r"9999998\s*=\s*Not ascertained",
        r"9999999\s*=\s*N/A",
    ):
        if not re.search(pattern, instructions, re.I):
            raise ReviewError("DDI family-income special codes changed")
    notes = [" ".join((n.text or "").split()) for n in root.iter() if _tag(n) == "notes"]
    if not any(re.search(r"sample that is part of this study:\s*1950 1%", n, re.I) for n in notes):
        raise ReviewError("DDI does not identify the selected 1950 1% sample")
    dates = {n.get("date") for n in root.iter() if _tag(n) == "timePrd"}
    if dates != {"1950"}:
        raise ReviewError("DDI extract is not restricted to 1950")
    names_in_file = [(n.text or "").strip() for n in root.iter() if _tag(n) == "fileName"]
    if len(names_in_file) != 1:
        raise ReviewError("DDI data file identity is ambiguous")
    match = re.fullmatch(r"(usa_\d{5})\.(?:dat|csv)", names_in_file[0], re.I)
    if match is None:
        raise ReviewError("DDI data file identity is not a USA extract")
    return {
        "extract_id": match[1].lower(),
        "variables": tuple(names),
        "ddi_sha256": hashlib.sha256(blob).hexdigest(),
        "slwt_decimals": 2,
    }


def _integer(value: str) -> int:
    if not re.fullmatch(r"[+-]?\d+", value):
        raise ReviewError("nonintegral or missing field in extract")
    return int(value)


def _weight(value: str) -> Decimal:
    # IPUMS CSV exports already render the two implied decimal places.  Do not
    # divide a CSV value by 100 again; DDI dcml describes fixed-width coding.
    try:
        if not re.fullmatch(r"\d+(?:\.\d{1,2})?", value):
            raise ValueError
        weight = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ReviewError("invalid sample-line weight") from exc
    if not weight.is_finite() or weight < 0:
        raise ReviewError("invalid sample-line weight")
    return weight


def weighted_median(observations: list[Observation]) -> dict[str, object]:
    """Inverse empirical weighted CDF: smallest code with cumulative weight >= half."""
    if not observations or any(o.weight <= 0 for o in observations):
        raise ReviewError("weighted median requires positive-weight observations")
    weights_by_income: dict[int, Decimal] = {}
    for observation in observations:
        weights_by_income[observation.income] = (
            weights_by_income.get(observation.income, Decimal()) + observation.weight
        )
    total = sum(weights_by_income.values(), Decimal())
    cumulative = Decimal()
    for value in sorted(weights_by_income):
        below = cumulative
        cumulative += weights_by_income[value]
        if cumulative * 2 >= total:
            return {
                "median_code": value,
                "weight_below": str(below),
                "weight_at_or_below": str(cumulative),
                "total_weight": str(total),
                "half_rank_exact_boundary": cumulative * 2 == total,
                "bottom_code_is_net_loss": value == -1,
                "top_code_reached": value == TOP_CODE,
            }
    raise ReviewError("weighted median rank was not reached")


def aggregate(records: csv.DictReader, names: tuple[str, ...]) -> dict[str, object]:
    """Process rows internally and return only national aggregate statistics."""
    header = records.fieldnames
    if header is None or len(header) != len(set(header)) or set(header) != set(names):
        raise ReviewError("CSV header does not match the DDI")
    if not REQUIRED.issubset(header):
        raise ReviewError("CSV header lacks required variables")
    seen_records: set[tuple[int, int]] = set()
    head_counts: Counter[int] = Counter()
    primary_unit_counts: Counter[int] = Counter()
    candidate_heads: list[tuple[int, dict[str, str]]] = []
    counts: Counter[str] = Counter(
        {
            key: 0
            for key in (
                "four_person_primary_heads",
                "primary_unit_size_mismatch",
                "ambiguous_household_heads",
                "not_sample_line",
                "sample_line_heads",
                "geography_nonmetro",
                "geography_metro_indeterminate",
                "geography_outside_central_identified",
                "geography_central_city_indeterminate",
                "geography_central_city",
                "income_not_ascertained",
                "income_not_applicable",
                "valid_income",
                "net_loss_code",
                "top_code",
            )
        }
    )
    groups: dict[str, list[Observation]] = {
        "metro": [],
        "nonmetro": [],
        "outside_central_identified": [],
    }
    geo = {
        1: "nonmetro",
        2: "metro_indeterminate",
        3: "outside_central_identified",
        4: "central_city_indeterminate",
        5: "central_city",
    }
    for row in records:
        if None in row or any(row.get(k) is None for k in REQUIRED):
            raise ReviewError("malformed CSV record")
        if _integer(row["YEAR"]) != 1950 or _integer(row["SAMPLE"]) != SAMPLE_CODE:
            raise ReviewError("record outside the 1950 1% sample")
        serial, pernum = _integer(row["SERIAL"]), _integer(row["PERNUM"])
        if serial <= 0 or pernum <= 0 or (serial, pernum) in seen_records:
            raise ReviewError("invalid or duplicated person record")
        seen_records.add((serial, pernum))
        if _integer(row["FAMUNIT"]) == 1:
            primary_unit_counts[serial] += 1
        if _integer(row["RELATE"]) != 1:
            continue
        head_counts[serial] += 1
        if _integer(row["GQ"]) != 1 or _integer(row["FAMUNIT"]) != 1:
            continue
        if _integer(row["FAMSIZE"]) != 4:
            continue
        candidate_heads.append((serial, row))
    counts["ambiguous_household_heads"] = sum(
        1 for serial in {serial for serial, _ in candidate_heads} if head_counts[serial] > 1
    )
    for serial, row in candidate_heads:
        if head_counts[serial] > 1:
            continue
        if primary_unit_counts[serial] != 4:
            counts["primary_unit_size_mismatch"] += 1
            continue
        counts["four_person_primary_heads"] += 1
        weight = _weight(row["SLWT"])
        if weight == 0:
            counts["not_sample_line"] += 1
            continue
        counts["sample_line_heads"] += 1
        metro = _integer(row["METRO"])
        if metro not in geo:
            raise ReviewError("unrecognized metropolitan category")
        counts["geography_" + geo[metro]] += 1
        income = _integer(row["FTOTINC"])
        if income in MISSING_INCOME:
            counts["income_not_ascertained" if income == 9999998 else "income_not_applicable"] += 1
            continue
        if income < -1 or income > TOP_CODE:
            raise ReviewError("income code outside documented 1950 range")
        counts["valid_income"] += 1
        if income == -1:
            counts["net_loss_code"] += 1
        if income == TOP_CODE:
            counts["top_code"] += 1
        obs = Observation(income, weight)
        if metro in (3, 4, 5):
            groups["metro"].append(obs)
        if metro == 1:
            groups["nonmetro"].append(obs)
        if metro == 3:
            groups["outside_central_identified"].append(obs)
    result = {}
    for name, values in groups.items():
        if len(values) < MINIMUM_CELL:
            raise ReviewError("headline group disclosure threshold not met")
        result[name] = {"unweighted_count": len(values), **weighted_median(values)}
    # Complementary suppression prevents deriving a rare diagnostic through
    # subtraction from a related total. Zero remains explicit; all nonzero
    # diagnostic cells are withheld if any is below the disclosure threshold.
    suppress = any(0 < value < MINIMUM_CELL for value in counts.values())
    withheld = sorted(key for key, value in counts.items() if suppress and value)
    safe_counts = {key: None if key in withheld else value for key, value in sorted(counts.items())}
    return {"counts": safe_counts, "suppressed_counts": withheld, "groups": result}


def run(csv_path: Path, ddi_path: Path, documentation: dict[str, Path]) -> dict[str, object]:
    if set(documentation) != set(DOC_PINS):
        raise ReviewError("missing pinned IPUMS documentation")
    doc_hashes = {}
    for key, expected_hash in DOC_PINS.items():
        digest = hashlib.sha256(documentation[key].read_bytes()).hexdigest()
        if digest != expected_hash:
            raise ReviewError("IPUMS documentation pin changed")
        doc_hashes[key] = digest
    metadata = validate_ddi(ddi_path.read_bytes())
    expected = str(metadata["extract_id"])
    filename = csv_path.name.lower()
    if filename not in {f"{expected}.csv", f"{expected}.csv.gz"}:
        raise ReviewError("CSV filename does not match DDI extract identity")
    # Hash and parse the same bytes: a file change between two opens cannot
    # bind the published aggregate to a different extract. Raw bytes remain
    # in memory only; neither raw data nor identifying rows are written.
    source_bytes = csv_path.read_bytes()
    data_hash = hashlib.sha256(source_bytes).hexdigest()
    raw = io.BytesIO(source_bytes)
    binary = gzip.GzipFile(fileobj=raw) if filename.endswith(".gz") else raw
    with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as stream:
        result = aggregate(csv.DictReader(stream, strict=True), metadata["variables"])
    return {
        "extract_id": expected,
        "ddi_sha256": metadata["ddi_sha256"],
        "data_sha256": data_hash,
        "sample": "1950 1%",
        "income_reference_year": 1949,
        "unit": "nominal USD, reported income-category midpoints",
        "population": (
            "IPUMS primary family units of four people in GQ=1 households with a sample-line head"
        ),
        "selection": (
            "RELATE=1; FAMUNIT=1; head FAMSIZE=4; four FAMUNIT=1 records per household; "
            "GQ=1; unique household head; SLWT>0"
        ),
        "weight": (
            "SLWT CSV decimal value; DDI fixed-width field has two implied decimals; "
            "no second division"
        ),
        "median_rule": (
            "smallest ordered value whose cumulative SLWT is at least half the total; "
            "no interpolation"
        ),
        "geography": (
            "METRO 1 nonmetro; 2 indeterminable/excluded; 3 outside central city; "
            "4 city status indeterminable; 5 central city; metro combines 3, 4, 5"
        ),
        "income_codes": (
            "0 is no income; -1 is a net-loss category, not a literal dollar amount; "
            "9999998/9999999 are missing; 10000 is top-coded"
        ),
        "limitations": (
            "FTOTINC covers primary family income as available for the sample-line head; "
            "income below age 14 is not included. IPUMS family-unit definitions can "
            "differ from Census family definitions; this is not all CPS families. "
            "The identifiable outside-central-city "
            "subset excludes metropolitan households with undetermined central-city status."
        ),
        "source_documentation": DOCS,
        "documentation_sha256": doc_hashes,
        **result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--ddi", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ftotinc-doc", type=Path, required=True)
    parser.add_argument("--slwt-doc", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.resolve() in {
            args.csv.resolve(),
            args.ddi.resolve(),
            args.ftotinc_doc.resolve(),
            args.slwt_doc.resolve(),
        }:
            raise ReviewError("output must differ from source files")
        result = run(args.csv, args.ddi, {"ftotinc": args.ftotinc_doc, "slwt": args.slwt_doc})
    except (ReviewError, OSError, csv.Error, UnicodeError) as exc:
        # Do not emit exceptions that could contain microdata, paths, or keys.
        print(f"Aggregate review failed: {type(exc).__name__}")
        return 1
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Wrote national aggregate-only family-income review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
