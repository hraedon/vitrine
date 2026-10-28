"""Qualify four modern compound food records from original CEX tables.

Curator-only readers: pypdf and openpyxl. No formula cache or missing table
cell is treated as an observation. Published means can be independently
rounded, so an absent food-away value is not inferred by subtraction.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tomllib
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PINS = {
    1985: "5d5375b8b207572d9fa5caded4a6ebaad9e0c2b966dcb7bad9534d70143fb82c",
    1996: "f85753e37acc96a31070183e18db7993c52613149df550c3469d9e3f9ba5eca5",
    2005: "09571721f46ca8af45a1dd398a74e44c743507134047f7a2da7cf209ba18127e",
    2013: "1636828737a1a8df29ac173dbffd8a072267e7f958f34d0eef4a9c851d8e0353",
}
FIELDS = {
    "total": "Average annual expenditures", "food": "Food", "home": "Food at home",
    "away": "Food away from home", "meat": "Meats, poultry, fish, and eggs",
    "cereals": "Cereals and bakery products", "dairy": "Dairy products",
    "produce": "Fruits and vegetables", "beef": "Beef", "milk": "Fresh milk and cream",
    "housing": "Housing", "transportation": "Transportation",
    "insurance": "Personal insurance and pensions", "healthcare": "Health care",
    "entertainment": "Entertainment", "apparel": "Apparel and services",
    "cash": "Cash contributions", "education": "Education",
}


def pdf_row(text: str, label: str, column: int) -> tuple[int | None, str]:
    rows = re.findall(r"^" + re.escape(label) + r"[: .]+(\$?\d.*)$", text, re.MULTILINE)
    if len(rows) != 1:
        raise ValueError(f"source row is missing or ambiguous: {label}")
    values = rows[0].split()
    if len(values) != 7:
        if column >= len(values) and all(re.fullmatch(r"\$?[\d,]+", v) for v in values):
            return None, rows[0]
        raise ValueError(f"source row has unexpected columns: {label}")
    if not all(re.fullmatch(r"\$?[\d,]+", value) for value in values):
        raise ValueError("source amount is not an unambiguous integer-dollar mean")
    return int(values[column].replace("$", "").replace(",", "")), rows[0]


def extract(samples: Path) -> dict[str, object]:
    from pypdf import PdfReader

    results: dict[str, object] = {}
    for year in (1985, 1996, 2005, 2013):
        name = f"02-cex/cusize-{year}.pdf" if year != 2013 else "19-cpi-tables/cu-size-2013.xlsx"
        blob = (samples / name).read_bytes()
        if hashlib.sha256(blob).hexdigest() != PINS[year]:
            raise ValueError(f"original CEX source changed: {year}")
        fields: dict[str, int | None] = {}
        source_rows: dict[str, str] = {}
        published_shares: dict[str, float] = {}
        if year != 2013:
            pages = PdfReader(io.BytesIO(blob)).pages
            text = "\n".join(page.extract_text() or "" for page in pages)
            if str(year) not in text[:200] or "consumer unit" not in text[:200]:
                raise ValueError("CEX year or population context changed")
            if "Four\npersons" not in text:
                raise ValueError("the four-person header is missing")
            column = 4 if year == 1985 else 5
            source_header = text.split("Number of consumer units", 1)[0].strip()
            end = re.search(r"^Personal insurance and pensions[ .]+\d.*$", text, re.MULTILINE)
            if end is None:
                raise ValueError("the expenditure section boundary is missing")
            text = text[:end.end()]
            for key, label in FIELDS.items():
                if year == 2005 and key == "healthcare":
                    label = "Healthcare"
                fields[key], source_rows[key] = pdf_row(text, label, column)
        else:
            import openpyxl

            book = openpyxl.load_workbook(io.BytesIO(blob), read_only=False, data_only=False)
            try:
                sheet = book["Table 1400"]
                if "Annual expenditure means" not in sheet["A1"].value:
                    raise ValueError("CEX table variant changed")
                if sheet["G4"].value != "Four\npeople":
                    raise ValueError("CEX population column changed")
                source_header = sheet["A1"].value + " | " + sheet["G4"].value
                for key, label in FIELDS.items():
                    if key == "healthcare":
                        label = "Healthcare"
                    rows = [
                        row for row in range(55, 600)
                        if sheet.cell(row, 1).value == label
                    ]
                    if len(rows) != 1 or sheet.cell(rows[0] + 1, 1).value != "Mean":
                        raise ValueError(f"CEX mean row changed: {label}")
                    cell = sheet.cell(rows[0] + 1, 7)
                    if cell.data_type == "f" or not isinstance(cell.value, int | float):
                        raise ValueError("CEX amount is not a literal source mean")
                    if int(cell.value) != cell.value:
                        raise ValueError("CEX amount is not a whole-dollar source mean")
                    fields[key] = int(cell.value)
                    source_rows[key] = cell.coordinate
                    share_cell = sheet.cell(rows[0] + 2, 7)
                    if sheet.cell(rows[0] + 2, 1).value == "Share":
                        if share_cell.data_type == "f":
                            raise ValueError("published CEX share is a formula cache")
                        published_shares[key] = float(share_cell.value)
            finally:
                book.close()
        results[str(year)] = {
            "year": str(year), "source_sha256": PINS[year], "file": name,
            "population": "Four-person consumer units", "statistic": "Annual expenditure means",
            "source_header": source_header,
            "values": fields, "source_rows": source_rows, "published_shares": published_shares,
        }
        results[str(year)]["placard"] = render(results[str(year)], year)
        results[str(year)]["budget_placard"] = render_budget(results[str(year)], year)
    return results


def render(record: dict[str, object], year: int) -> str:
    values = record["values"]
    share = (Decimal(values["food"]) * 100 / Decimal(values["total"])).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP,
    )
    value = f'Food ${values["food"]:,}/yr ({share:.1f}% of expenditure). '
    value += f'Food at home ${values["home"]:,}. '
    if values["away"] is None:
        value += "Food away from home: no value printed in the archived column. "
    else:
        value += f'Food away from home ${values["away"]:,}. '
    order = ["meat", "cereals", "dairy", "produce", "beef", "milk"] if year == 1985 else (
        ["meat", "cereals", "produce", "dairy", "beef"] if year == 1996 else
        ["meat", "produce", "cereals", "dairy", "beef"]
    )
    labels = {
        "meat": "meats/poultry/fish/eggs", "cereals": "cereals/bakery", "dairy": "dairy",
        "produce": "fruits/vegetables", "beef": "beef", "milk": "fresh milk and cream",
    }
    value += "Key items: " + ", ".join(f'{labels[key]} ${values[key]:,}' for key in order)
    return value + f'. Total expenditure: ${values["total"]:,}.'


def render_budget(record: dict[str, object], year: int) -> str:
    values = record["values"]
    keys = ["housing", "transportation", "food", "insurance"] + (
        ["healthcare", "entertainment"] if year == 2013 else ["entertainment", "healthcare"]
    ) + ["apparel", "cash", "education"]
    labels = {
        "housing": "Housing", "transportation": "transportation", "food": "food",
        "insurance": "insurance/pensions", "healthcare": "healthcare",
        "entertainment": "entertainment", "apparel": "apparel",
        "cash": "cash contributions", "education": "education",
    }
    parts: list[str] = []
    for key in keys:
        if year == 2013:
            share = Decimal(str(record["published_shares"][key]))
        else:
            share = (Decimal(values[key]) * 100 / Decimal(values["total"])).quantize(
                Decimal("0.1"), rounding=ROUND_HALF_UP,
            )
        parts.append(f"{labels[key]} {share:.1f}%")
    return ", ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=REPO / "samples")
    parser.add_argument("--data", type=Path, default=REPO / "data")
    args = parser.parse_args()
    results = extract(args.samples)
    for year in (1985, 1996, 2005, 2013):
        decade = f"{year // 10 * 10}s"
        data = tomllib.loads((args.data / "us" / f"{decade}.toml").read_text(encoding="utf-8"))
        fact = next(f for f in data["fact"] if f["id"] == f"us-{decade}-food-basket")
        if fact["value"] != render(results[str(year)], year):
            raise ValueError(f"compound food placard disagrees with original source: {year}")
        budget = next(f for f in data["fact"] if f["id"] == f"us-{decade}-expenditure-shares")
        if budget["value"] != render_budget(results[str(year)], year):
            raise ValueError(f"compound budget placard disagrees with original source: {year}")
    destination = args.samples / "59-workbook-review/cex-food-observations.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Qualified four compound food records against original CEX PDF/XLSX cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
