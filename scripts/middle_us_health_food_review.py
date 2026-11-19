"""Reproduce CMS compounds and ERS displayed availability from pinned originals.

Curator-only XLSX reading needs openpyxl. ERS cached formula values are never
accepted alone: the selected supply/use formulas are replayed from literal
inputs and compared with the cache before applying the publisher's cell format.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import tomllib
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PINS = {
    "23-cms-health-expenditure/NHE24_Summary.csv":
        "8642644377858cc6a9fe2d09bf63e89a03282c5e43501a414fc649dacb1a765d",
    "23-cms-health-expenditure/NHE2024.csv":
        "74e80287bb5e946ad9f2637ee708266988716d2991af93ee0dc6e9c5747a3df3",
    "46-diet-variety/ers-fads-fruit-fresh.xlsx":
        "6988e35a4a4b8700a6f9255de0e29708afc01f91662ce28394973a0cc740069c",
    "46-diet-variety/ers-fads-vegetables-fresh.xlsx":
        "199e19b8fe8f24279949a02a7053f8d761bccb2dd0b425d71753d34444e0108e",
}
YEARS = (1960, 1970, 1980, 1990, 2000, 2010, 2024)
SUMMARY = {
    "nhe_billions": (3, "National Health Expenditures (Amount in Billions)"),
    "population_millions": (9, "U.S. Population1 (Millions)"),
    "gdp_billions": (10, "Gross Domestic Product2  (Amount in Billions)"),
    "per_capita": (25, "National Health Expenditures (Per Capita Amount)"),
    "personal_per_capita": (27, "Personal Health Care"),
    "gdp_share": (
        31, "National Health Expenditures as a Percent of Gross Domestic Product (Percent)",
    ),
}
DETAIL = {
    "total": (3, "Total National Health Expenditures"), "out_of_pocket": (4, "Out of pocket"),
    "medicare": (7, "Medicare"), "medicaid": (8, "Medicaid (Title XIX)"),
    "medicaid_federal": (9, "Federal"), "medicaid_state_local": (10, "State and Local"),
    "hospital": (103, "Total Hospital Expenditures"),
    "prescription_drugs": (283, "Total Prescription Drug Expenditures"),
}


def number(value: object) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError("missing literal numeral")
    text = str(value).strip().replace(",", "")
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        raise ValueError(f"not a literal numeral: {value!r}")
    return Decimal(text)


def rounded(value: Decimal, places: int) -> str:
    return format(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP), "f")


def cms_extract(summary: bytes, detail: bytes) -> dict[str, object]:
    tables = [list(csv.reader(io.StringIO(blob.decode(encoding), newline="")))
              for blob, encoding in ((summary, "utf-8-sig"), (detail, "cp1252"))]
    if "Calendar Years 1960-2024" not in tables[0][0][0]:
        raise ValueError("CMS summary title changed")
    if "CALENDAR YEARS 1960 to 2024" not in tables[1][0][0]:
        raise ValueError("CMS detail title changed")
    results: dict[str, object] = {}
    for year in YEARS:
        record: dict[str, object] = {"year": str(year)}
        for rows, fields in zip(tables, (SUMMARY, DETAIL), strict=True):
            columns = [i for i, item in enumerate(rows[1]) if item == str(year)]
            if len(columns) != 1:
                raise ValueError("CMS year column absent or ambiguous")
            column = columns[0]
            for key, (row, label) in fields.items():
                if rows[row - 1][0].strip() != label:
                    raise ValueError(f"CMS source category changed: {key}")
                raw = rows[row - 1][column].strip()
                record[key] = None if raw == "-" else format(number(raw), "f")
                record[key + "_cell"] = f"R{row}:C{column + 1}"
        results[str(year)] = record
    return results


def cms_value(
    record: dict[str, object], kind: str, baseline: dict[str, object] | None = None,
) -> str:
    def get(key: str) -> Decimal:
        return number(record[key])

    def cash(key: str, places: int = 0) -> str:
        return f"${get(key):,.{places}f}"

    def share(key: str) -> str:
        return rounded(get(key) / get("total") * 100, 1)

    if kind == "total":
        return f"{cash('nhe_billions', 1)} billion ({get('gdp_share'):.1f}% of GDP)"
    if kind == "per-capita":
        return (f"{cash('per_capita')} per capita "
                f"({cash('personal_per_capita')} for personal health care)")
    if kind == "out-of-pocket-share":
        return f"{share('out_of_pocket')}% of national health expenditures paid out of pocket"
    if kind == "gdp-share-arc":
        if baseline is None or baseline["year"] != "1960":
            raise ValueError("GDP comparison requires the original 1960 baseline row")
        return f"{number(baseline['gdp_share']):.1f}% (1960) → {get('gdp_share'):.1f}% (2024)"
    key = kind.replace("-", "_")
    if key not in {"medicare", "medicaid", "hospital", "prescription_drugs"}:
        raise ValueError("unknown CMS exhibit")
    if record[key] is None:
        return f"Not reported for {record['year']} — the source prints a dash"
    result = f"{cash(key)} million ({share(key)}% of NHE)"
    if key == "medicaid" and record["year"] in {"1970", "2024"}:
        result += (f"; Federal {cash('medicaid_federal')}M, "
                   f"State/Local {cash('medicaid_state_local')}M")
    return result


def farm_row(sheet: object, cached: object, row: int, fruit: bool) -> dict[str, object]:
    """Replay only the inspected source formulas; never execute workbook code."""
    def cell(column: str) -> object:
        value = sheet[f"{column}{row}"].value
        if isinstance(value, str) and value.startswith("="):
            raise ValueError("expected a literal supply/use input")
        return value

    def literal(column: str) -> Decimal:
        return number(cell(column))

    production, imports = cell("C"), cell("D")
    supply_formula = sheet[f"E{row}"].value
    if supply_formula == f"=SUM(C{row},D{row})":
        # Excel SUM ignores source text; do not apply this rule to arithmetic
        # or infer that an unavailable observation itself equals zero.
        supply = sum((number(v) for v in (production, imports) if v != "NA"), Decimal())
    elif supply_formula == f"=C{row}+D{row}":
        supply = number(production) + number(imports)
    else:
        raise ValueError("uninspected supply formula")
    total_column, farm_column = ("H", "I") if fruit else ("G", "H")
    total_formula = sheet[f"{total_column}{row}"].value
    if total_formula == f"=E{row}-F{row}":
        food = supply - literal("F")
    elif fruit and total_formula == f"=E{row}-F{row}-G{row}":
        food = supply - literal("F") - literal("G")
    elif not fruit and total_formula == f"=E{row}-SUM(F{row})":
        food = supply - (Decimal() if cell("F") == "NA" else literal("F"))
    else:
        raise ValueError("uninspected food-availability formula")
    farm = sheet[f"{farm_column}{row}"]
    expected = f"=IF({total_column}{row}=0,0,IF(B{row}=0,0,{total_column}{row}/B{row}))"
    if farm.value != expected:
        raise ValueError("farm-weight ratio formula changed")
    population = literal("B")
    if population <= 0 or food < 0:
        raise ValueError("invalid supply or population")
    value = food / population
    cached_value = number(cached[f"{farm_column}{row}"].value)
    if abs(value - cached_value) > Decimal("0.0000000001"):
        raise ValueError("publisher formula cache does not reproduce literal operands")
    if farm.number_format not in {"0.00", "#,##0.00", "#,##0.0"}:
        raise ValueError("uninspected publisher display precision")
    places = 1 if farm.number_format == "#,##0.0" else 2
    return {
        "year": str(int(literal("A"))), "food_million_pounds": format(food, "f"),
        "population_millions": format(population, "f"), "value": rounded(value, places),
        "precision": places, "cell": f"{sheet.title}!{farm_column}{row}",
        "population_heading": str(sheet["B3" if fruit else "B4"].value),
        "supply_formula": supply_formula, "food_formula": total_formula,
        "farm_formula": farm.value, "number_format": farm.number_format,
    }


def extract(samples: Path) -> dict[str, object]:
    blobs = {}
    for path, expected in PINS.items():
        blob = (samples / path).read_bytes()
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError(f"original source hash changed: {path}")
        blobs[path] = blob
    cms = cms_extract(blobs[next(iter(PINS))], blobs[list(PINS)[1]])
    from openpyxl import load_workbook

    availability: dict[str, object] = {}
    for fruit in (False, True):
        path = list(PINS)[2 if fruit else 3]
        book = load_workbook(io.BytesIO(blobs[path]), data_only=False)
        cache = load_workbook(io.BytesIO(blobs[path]), data_only=True)
        try:
            for name, slug in (("Grapes", "grapes"), ("Avocados", "avocados")) if fruit else (
                ("Peppers", "bell-peppers"), ("Broccoli", "broccoli"),
            ):
                sheet = book[name]
                title = str(sheet["A1"].value)
                if "Supply and use" not in title or sheet["I4" if fruit else "H4"].value != "Farm":
                    raise ValueError("commodity or farm-weight heading changed")
                footnotes = [cell.value.strip() for row in sheet.iter_rows(min_col=1, max_col=1)
                             for cell in row if isinstance(cell.value, str)
                             and re.match(r"\d[A-Z]", cell.value)]
                population = [note for note in footnotes
                              if "Resident population plus the Armed Forces overseas" in note]
                if len(population) != 1:
                    raise ValueError("source population definition absent or ambiguous")
                for row in range(7, sheet.max_row + 1):
                    year = sheet[f"A{row}"].value
                    if year not in (1960, 1970, 1980, 1990, 2000, 2010, 2020):
                        continue
                    if fruit and (year == 1960 or (slug == "avocados" and year == 2020)):
                        continue
                    record = farm_row(sheet, cache[name], row, fruit)
                    record.update({
                        "file": path, "sha256": PINS[path], "title": title,
                        "population_definition": population[0], "footnotes": footnotes,
                    })
                    availability[f"us-{year}s-availability-{slug}"] = record
        finally:
            book.close()
            cache.close()
    return {"source_hashes": PINS, "cms": cms, "availability": availability}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=REPO / "samples")
    parser.add_argument(
        "--check", action="store_true", help="compare complete placards with originals",
    )
    args = parser.parse_args()
    result = extract(args.samples)
    if args.check:
        qualify(result, REPO / "data")
    destination = args.samples / "remaining-audit-20261028/middle-us-health-food.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Reproduced CMS and farm-weight source fields to {destination}")
    return 0


def qualify(result: dict[str, object], data: Path) -> None:
    count = 0
    for path in sorted((data / "us").glob("*.toml")):
        for fact in tomllib.loads(path.read_text(encoding="utf-8"))["fact"]:
            identifier = fact["id"]
            if fact["source"] == "cms-nhe":
                year = "2024" if path.stem == "2020s" else path.stem[:4]
                expected = cms_value(
                    result["cms"][year], identifier.split("-nhe-", 1)[1], result["cms"]["1960"],
                )
                if fact["value"] != expected:
                    raise ValueError(f"CMS compound placard differs from original: {identifier}")
                count += 1
            elif fact["source"] == "usda-ers-fads":
                observation = result["availability"][identifier]
                expected = f"{observation['value']} pounds per person per source year"
                if fact["value"] != expected or Decimal(str(fact["quantity"])) != number(
                    observation["value"]
                ):
                    raise ValueError(f"ERS placard differs from source display: {identifier}")
                count += 1
    if count != 68:
        raise ValueError("reviewed exhibit membership changed; inspect the qualifier scope")


if __name__ == "__main__":
    raise SystemExit(main())
