"""Extract published BTS vehicle shares and calculate their complements.

This curator artifact is derived from the publisher workbook, not a publisher
file. It refuses formulas in the used cells and binds title, year and row labels.
Requires openpyxl in the curator environment, not in the core runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from openpyxl import load_workbook

SHA = "7970889831564822da730bdd642f9973bed461a7430857588d460e287c5f2eb3"


def extract(path: Path) -> dict[str, object]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA:
        raise ValueError("BTS source workbook changed")
    sheet = load_workbook(path, data_only=False)["Figure 2-6"]
    if sheet["A1"].value != "FIGURE 2-6 Share of Households by Vehicles Available: 1960–2023":
        raise ValueError("BTS figure title changed")
    if [sheet[f"A{row}"].value for row in range(4, 8)] != [
        "0 vehicles",
        "1 vehicle",
        "2 vehicles",
        "3 or more vehicles",
    ]:
        raise ValueError("BTS vehicle categories changed")
    output = {}
    for col, year in (
        ("B", 1960), ("C", 1970), ("D", 1980),
        ("E", 1990), ("F", 2000), ("G", 2010),
    ):
        if sheet[f"{col}3"].value != year:
            raise ValueError("BTS year header changed")
        values = [sheet[f"{col}{row}"] for row in range(4, 8)]
        if any(
            cell.data_type == "f" or not isinstance(cell.value, (int, float)) for cell in values
        ):
            raise ValueError("BTS value is a formula or nonnumeric")
        no_vehicle = Decimal(str(values[0].value)) * 100
        output[str(year)] = {
            "no_vehicle_percent": str(no_vehicle.quantize(Decimal("0.1"))),
            "one_or_more_percent": str((Decimal(100) - no_vehicle).quantize(Decimal("0.1"))),
            "figure": "2-6",
            "population": "occupied housing units",
        }
    return {"provenance": "Curator complement from pinned BTS Figure 2-6", "years": output}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("workbook", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    args.output.write_text(
        json.dumps(extract(args.workbook), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
