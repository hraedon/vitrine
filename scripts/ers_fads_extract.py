#!/usr/bin/env python3
"""Regenerate curated USDA/ERS food-availability series from pinned workbooks.

Existing year windows are retained. Source formulas and cached results are
checked before applying each cell's published precision; source literals are
preserved when the publisher does not provide the supporting supply values.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import tomllib
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

if __package__:
    from .middle_us_health_food_review import PINS, farm_row
else:
    from middle_us_health_food_review import PINS, farm_row

REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / "samples" / "46-diet-variety"
OUT_DIR = REPO / "data" / "series"

VEG = ARCHIVE / "ers-fads-vegetables-fresh.xlsx"
FRUIT = ARCHIVE / "ers-fads-fruit-fresh.xlsx"

# slug -> (workbook, sheet, display label). The four WI-6a arc-group
# commodities keep their original slugs and labels so regeneration is
# byte-identical; the rest follow the same pattern.
COMMODITIES: dict[str, tuple[Path, str, str]] = {
    # ── vegetables, fresh ──
    "artichokes": (VEG, "Artichokes", "Fresh artichokes"),
    "asparagus": (VEG, "Asparagus", "Fresh asparagus"),
    "lima-beans": (VEG, "LimaBeans", "Fresh lima beans"),
    "snap-beans": (VEG, "SnapBeans", "Fresh snap beans"),
    "broccoli": (VEG, "Broccoli", "Fresh broccoli"),
    "brussels-sprouts": (VEG, "BrusselsSprouts", "Fresh Brussels sprouts"),
    "cabbage": (VEG, "Cabbage", "Fresh cabbage"),
    "carrots": (VEG, "Carrots", "Fresh carrots"),
    "cauliflower": (VEG, "Cauliflower", "Fresh cauliflower"),
    "celery": (VEG, "Celery", "Fresh celery"),
    "collards": (VEG, "Collards", "Fresh collards"),
    "sweet-corn": (VEG, "SweetCorn", "Fresh sweet corn"),
    "cucumbers": (VEG, "Cucumbers", "Fresh cucumbers"),
    "eggplant": (VEG, "Eggplant", "Fresh eggplant"),
    "escarole": (VEG, "Escarole", "Fresh escarole"),
    "garlic": (VEG, "Garlic", "Fresh garlic"),
    "head-lettuce": (VEG, "HeadLettuce", "Fresh head lettuce"),
    "kale": (VEG, "Kale", "Fresh kale"),
    "mushrooms": (VEG, "Mushrooms", "Fresh mushrooms"),
    "mustard-greens": (VEG, "MustardGreens", "Fresh mustard greens"),
    "okra": (VEG, "Okra", "Fresh okra"),
    "onions": (VEG, "Onions", "Fresh onions"),
    "bell-peppers": (VEG, "Peppers", "Fresh bell peppers"),
    "potatoes": (VEG, "Potatoes", "Fresh potatoes"),
    "pumpkin": (VEG, "Pumpkin", "Fresh pumpkin"),
    "radishes": (VEG, "Radishes", "Fresh radishes"),
    "romaine": (VEG, "Romaine", "Fresh romaine"),
    "spinach": (VEG, "Spinach", "Fresh spinach"),
    "squash": (VEG, "Squash", "Fresh squash"),
    "sweet-potatoes": (VEG, "SweetPotatoes", "Fresh sweet potatoes"),
    "tomatoes": (VEG, "Tomatoes", "Fresh tomatoes"),
    "turnip-greens": (VEG, "TurnipGreens", "Fresh turnip greens"),
    # ── fruit, fresh ──
    "grapefruit": (FRUIT, "Grapefruit", "Fresh grapefruit"),
    "lemons": (FRUIT, "Lemons", "Fresh lemons"),
    "limes": (FRUIT, "Limes", "Fresh limes"),
    "oranges": (FRUIT, "Oranges", "Fresh oranges"),
    "tangerines": (FRUIT, "Tangerines, etc.", "Fresh tangerines"),
    "apples": (FRUIT, "Apples", "Fresh apples"),
    "apricots": (FRUIT, "Apricots", "Fresh apricots"),
    "avocados": (FRUIT, "Avocados", "Fresh avocados"),
    "bananas": (FRUIT, "Bananas", "Fresh bananas"),
    "blueberries": (FRUIT, "Blueberries", "Fresh blueberries"),
    "cantaloupe": (FRUIT, "Cantaloupe", "Fresh cantaloupe"),
    "grapes": (FRUIT, "Grapes", "Fresh grapes"),
    "honeydew": (FRUIT, "Honeydew", "Fresh honeydew"),
    "kiwifruit": (FRUIT, "Kiwifruit", "Fresh kiwifruit"),
    "mangoes": (FRUIT, "Mangoes", "Fresh mangoes"),
    "papayas": (FRUIT, "Papayas", "Fresh papayas"),
    "peaches": (FRUIT, "Peaches", "Fresh peaches"),
    "pears": (FRUIT, "Pears", "Fresh pears"),
    "pineapples": (FRUIT, "Pineapples", "Fresh pineapples"),
    "raspberries": (FRUIT, "Raspberries", "Fresh raspberries"),
    "strawberries": (FRUIT, "Strawberries", "Fresh strawberries"),
    "watermelon": (FRUIT, "Watermelon", "Fresh watermelon"),
}


def _pin(path: Path) -> None:
    key = f"46-diet-variety/{path.name}"
    if hashlib.sha256(path.read_bytes()).hexdigest() != PINS[key]:
        raise ValueError(f"Original workbook differs from the inspected source: {path.name}")


def _layout(sheet: object) -> tuple[int, int, int, int, str, str, str]:
    header = next(
        (i for i in range(1, 8) if str(sheet.cell(i, 1).value or "").strip().startswith("Year")),
        None,
    )
    if header is None:
        raise ValueError("year heading absent")
    head = [str(sheet.cell(header, i).value or "").strip() for i in range(1, sheet.max_column + 1)]
    pop = [i + 1 for i, v in enumerate(head) if "population" in v.lower()]
    if len(pop) != 1:
        raise ValueError("population heading absent or ambiguous")
    availability = []
    for i in range(max(1, header - 3), header):
        availability.extend(
            j
            for j in range(1, sheet.max_column + 1)
            if str(sheet.cell(i, j).value or "").startswith("Food availability")
        )
    if len(availability) != 1:
        raise ValueError("food availability heading absent or ambiguous")
    farm = [
        j
        for i in (header, header + 1)
        for j in range(1, sheet.max_column + 1)
        if sheet.cell(i, j).value == "Farm"
    ]
    if len(farm) != 1 or farm[0] <= availability[0]:
        raise ValueError("farm-weight heading absent, ambiguous, or out of order")
    notes = [
        str(sheet.cell(i, 1).value).strip()
        for i in range(1, sheet.max_row + 1)
        if isinstance(sheet.cell(i, 1).value, str)
    ]
    population = [
        n for n in notes if re.search(r"Resident population plus (?:the )?Armed Forces overseas", n)
    ]
    if len(population) != 1:
        raise ValueError("population definition absent or ambiguous")
    conversion = next(
        (
            str(sheet.cell(i, j).value).strip()
            for i in range(header, header + 4)
            for j in range(1, sheet.max_column + 1)
            if str(sheet.cell(i, j).value or "").startswith("CF =")
        ),
        "",
    )
    marketing = [n for n in notes if "marketing" in n.lower() and re.match(r"\d", n)]
    heading = re.sub(r"(?:(?<=1)|(?<=year))[1-9]$", "", head[pop[0] - 1]).strip()
    return (
        header,
        pop[0],
        availability[0],
        farm[0],
        conversion,
        heading,
        " ".join(re.sub(r"^\d+", "", note).strip() for note in marketing),
    )


def _formula_value(
    sheet: object, address: str, row: int, seen: frozenset[str] = frozenset()
) -> Decimal | str:
    if address in seen or not re.fullmatch(rf"[A-Z]+{row}", address):
        raise ValueError(f"cycle or cross-row reference: {address}")
    value = sheet[address].value
    if value is None or value == "NA":
        return "NA"
    if isinstance(value, bool):
        raise ValueError("boolean is not a source numeral")
    if not isinstance(value, str) or not value.startswith("="):
        try:
            number = Decimal(str(value))
        except Exception as exc:
            raise ValueError(f"unexpected literal in {address}") from exc
        if not number.is_finite():
            raise ValueError("nonfinite source numeral")
        return number
    expr = value[1:]
    expr = re.sub(
        r"([A-Z]+\d+):([A-Z]+\d+)",
        lambda m: (
            ",".join(
                f"{get_column_letter(i)}{row}"
                for i in range(sheet[m[1]].column, sheet[m[2]].column + 1)
            )
            if re.fullmatch(rf"[A-Z]+{row}", m[1]) and re.fullmatch(rf"[A-Z]+{row}", m[2])
            else "INVALID_RANGE"
        ),
        expr,
    )
    expr = re.sub(r"(?<![<>=])=(?!=)", "==", expr)
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"unsupported source formula in {address}") from exc

    def evaluate(node: ast.AST) -> Decimal | str | bool:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(str(node.value))
        if isinstance(node, ast.Name):
            return _formula_value(sheet, node.id, row, seen | {address})
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Div)):
            left, right = evaluate(node.left), evaluate(node.right)
            if not isinstance(left, Decimal) or not isinstance(right, Decimal):
                raise ValueError("missing source value used outside SUM")
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            return left / right
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
            return evaluate(node.left) == evaluate(node.comparators[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "SUM" and not node.keywords:
                items = [evaluate(arg) for arg in node.args]
                if any(not isinstance(v, Decimal) and v != "NA" for v in items):
                    raise ValueError("unexpected value in SUM")
                return sum((v for v in items if isinstance(v, Decimal)), Decimal())
            if node.func.id == "IF" and len(node.args) == 3 and not node.keywords:
                condition = evaluate(node.args[0])
                if not isinstance(condition, bool):
                    raise ValueError("IF condition is not a comparison")
                return evaluate(node.args[1] if condition else node.args[2])
        raise ValueError(f"unsupported formula syntax in {address}")

    return evaluate(tree.body)  # type: ignore[return-value]


def parse(
    workbook: Path, sheet_name: str, years: set[int], formula: object, cache: object
) -> tuple[dict[int, str], str, str, str]:
    """Read only the existing curated years, respecting every source cell format."""
    s, cached = formula[sheet_name], cache[sheet_name]
    if "Supply and use" not in str(s["A1"].value):
        raise ValueError("commodity title changed")
    header, _pop, _availability, farm, conversion, heading, marketing = _layout(s)
    out: dict[int, str] = {}
    for row in range(header + 1, s.max_row + 1):
        year_value = s.cell(row, 1).value
        if isinstance(year_value, bool) or not re.fullmatch(r"\d{4}", str(year_value)):
            continue
        year = int(year_value)
        if year not in years:
            continue
        address = f"{get_column_letter(farm)}{row}"
        cell = s[address]
        fmt = cell.number_format
        match = re.fullmatch(r"(?:#,##)?0\.(0+)", fmt)
        if not match:
            raise ValueError(f"uninspected source precision: {sheet_name} {year}: {fmt}")
        places = len(match[1])
        source_value = _formula_value(s, address, row)
        if not isinstance(source_value, Decimal):
            raise ValueError(f"missing farm value: {sheet_name} {year}")
        cached_value = Decimal(str(cached[address].value))
        if abs(source_value - cached_value) > Decimal("0.0000000001"):
            raise ValueError(f"source formula cache differs: {sheet_name} {year}")
        # Four principal exhibits also replay the source-family qualifier.
        if sheet_name in {"Avocados", "Grapes", "Broccoli", "Peppers"}:
            qualified = farm_row(s, cached, row, workbook == FRUIT)
            if Decimal(str(qualified["value"])) != source_value.quantize(
                Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP
            ):
                raise ValueError("independent source qualifier differs")
        if year in out:
            raise ValueError("duplicate source year")
        out[year] = format(
            source_value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP), "f"
        )
    if set(out) != years:
        raise ValueError(f"source years changed: {sheet_name}: {sorted(years - set(out))}")
    return out, conversion, heading, marketing


def render_toml(
    slug: str, label: str, values: dict[int, str], conversion: str, heading: str, marketing: str
) -> str:
    years = sorted(values)
    note = (
        "Fresh food availability is production plus imports, less exports and other "
        "specified uses, per person. This is a supply measure, not intake. "
        f"The source population reference is {heading}; it includes resident population "
        "and Armed Forces overseas. Values use the source cell's displayed precision, "
        "after replaying source formulas and checking their caches where formulas are present; "
        "published literal cells remain literal. "
        f"The separate retail-weight conversion ({conversion or 'see source sheet'}) "
        "is not applied. These are the selected curated years, not a claim about "
        "the first or last year available from ERS."
    )
    if marketing:
        note += " Source marketing-period note: " + marketing
    series_label = f"{label} available per person, {years[0]}-{years[-1]}"
    lines = [
        "# Auto-generated from pinned USDA/ERS food-availability workbooks.",
        "",
        "[[series]]",
        f'id = "us-availability-{slug}"',
        f"label = {json.dumps(series_label, ensure_ascii=False)}",
        'source = "usda-ers-fads"',
        'tier = "A"',
        'unit = "pounds per person per source year (farm weight)"',
        'population = "U.S. resident population plus Armed Forces overseas; supply-side average"',
        f"notes = {json.dumps(note, ensure_ascii=False)}",
        "",
        "[series.values]",
    ]
    lines.extend(f"{year} = {values[year]}" for year in years)
    return "\n".join(lines) + "\n"


def main() -> None:
    books = {}
    prepared = []
    try:
        for workbook in (VEG, FRUIT):
            _pin(workbook)
            books[workbook] = (
                load_workbook(workbook, data_only=False),
                load_workbook(workbook, data_only=True),
            )
        for slug, (workbook, sheet, label) in COMMODITIES.items():
            path = OUT_DIR / f"us-availability-{slug}.toml"
            existing = tomllib.loads(path.read_text(encoding="utf-8"))["series"][0]["values"]
            values, conversion, heading, marketing = parse(
                workbook, sheet, {int(y) for y in existing}, *books[workbook]
            )
            prepared.append(
                (path, render_toml(slug, label, values, conversion, heading, marketing))
            )
            print(f"{slug}: {len(values)} selected years, source-formula and format checked")
        for path, content in prepared:
            path.write_text(content, encoding="utf-8", newline="\n")
    finally:
        for formula, cache in books.values():
            formula.close()
            cache.close()


if __name__ == "__main__":
    main()
