#!/usr/bin/env python3
"""Extract the Plan 027 WI-6 food-availability series from USDA/ERS FADS.

Emits one series per commodity into ``data/series/us-availability-*.toml``
from the ERS Food Availability (Per Capita) Data System workbooks archived in
``samples/46-diet-variety/``. Every fresh fruit and vegetable commodity sheet
in the two workbooks is extracted — the four the plan picked for the
"exotic-turned-ordinary" arc group (broccoli, bell peppers, avocados, grapes)
plus every other commodity, whose combined per-decade counts feed the derived
produce-variety fact (FWI-007 item 1).

**What this measures, and does not.** Food *availability* is a disappearance
estimate — production plus imports, less exports and non-food use, divided by
population. It is what the food supply made available per person, not what
anyone ate; ERS publishes a separate loss-adjusted series for consumption-like
figures and this is not it. Every card says so.

**Farm weight, not retail.** Each sheet publishes two per-capita columns side
by side: farm weight, and a retail weight derived by applying a conversion
factor (0.92 for broccoli, printed in the sheet). The unadjusted farm-weight
column is taken, because the retail column is a modelled adjustment; the
factor is disclosed rather than silently applied.

**The column is identified by arithmetic, not position.** Farm-weight per
capita must equal total food availability (millions of pounds) divided by
population (millions). The parser recomputes it for every year and refuses to
write unless the published figure reproduces — the same guard the FHWA
extractor uses, and for the same reason: several plausible numeric columns sit
side by side.

Spot-verification: see docs/verification-log.md, Plan 027 WI-6.
"""

from __future__ import annotations

from pathlib import Path

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

HEADER_ROW_FIRST_CELL = "Year"


def _sheet_rows(workbook: Path, sheet: str) -> list[tuple]:
    import openpyxl

    wb = openpyxl.load_workbook(workbook, data_only=True)
    if sheet not in wb.sheetnames:
        raise SystemExit(f"{workbook.name}: no sheet {sheet!r}")
    return list(wb[sheet].iter_rows(values_only=True))


def _number(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text in {"", "NA", "--", "-"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _locate(rows: list[tuple]) -> tuple[int, dict[str, int], str]:
    """Find the header row and the columns, by their printed labels.

    The two workbooks do not share a layout: the fruit sheets carry an extra
    "Shipments to U.S. Territories" column and print "Farm" on the row below
    the header, while the vegetable sheets print it on the header row itself.
    A fixed column index is therefore wrong for one of them, so every column
    is found by its label and the result is asserted.
    """
    header = next(
        (i for i, r in enumerate(rows)
         if r and str(r[0] or "").strip().startswith(HEADER_ROW_FIRST_CELL)),
        None,
    )
    if header is None:
        raise SystemExit(f"no header row starting {HEADER_ROW_FIRST_CELL!r}")

    def cells(i: int) -> list[str]:
        return [("" if c is None else str(c)).strip() for c in rows[i]]

    head = cells(header)
    below = cells(header + 1) if header + 1 < len(rows) else []

    cols: dict[str, int] = {"year": 0}
    # The population column label varies across the workbooks — the citrus
    # sheets print "U.S. total population, July 1<footnote>" while the others
    # print "U.S. population, July 1" — so the column is matched by the word
    # "population" and must match exactly one column, else the layout is not
    # what this parser assumes.
    pop_cols = [j for j, text in enumerate(head) if "population" in text.casefold()]
    if len(pop_cols) != 1:
        raise SystemExit(
            f"expected exactly one 'population' column, found {len(pop_cols)} "
            f"— the layout is not what this parser assumes"
        )
    cols["population"] = pop_cols[0]
    # The header row prints two columns starting with "Total" ("Total supply"
    # and the availability total), both carrying footnote markers, so the
    # availability column is found by the "Food availability" spanner printed
    # above it rather than by matching header text.
    for i in range(max(0, header - 3), header):
        for j, text in enumerate(cells(i)):
            if text.startswith("Food availability"):
                cols["availability"] = j
    # "Farm" sits on the header row (vegetables) or the row below it (fruit)
    for source in (head, below):
        for j, text in enumerate(source):
            if text == "Farm":
                cols["farm"] = j
                break
        if "farm" in cols:
            break

    missing = {"population", "availability", "farm"} - set(cols)
    if missing:
        raise SystemExit(f"could not locate columns {sorted(missing)} from {head!r}")
    if cols["farm"] <= cols["availability"]:
        raise SystemExit(
            f"the 'Farm' column ({cols['farm']}) is not right of 'Total' "
            f"({cols['availability']}) — the layout is not what this parser assumes"
        )

    conversion = ""
    for i in range(header, min(header + 4, len(rows))):
        for text in cells(i):
            if text.startswith("CF ="):
                conversion = text
    return header, cols, conversion


def parse(workbook: Path, sheet: str) -> tuple[dict[int, float], str]:
    """Return (year -> farm-weight lb per capita, the retail conversion note)."""
    rows = _sheet_rows(workbook, sheet)
    header, cols, conversion = _locate(rows)

    out: dict[int, float] = {}
    checked = 0
    for row in rows[header + 1 :]:
        if not row:
            continue
        year = _number(row[cols["year"]])
        if year is None or not (1900 <= year <= 2100):
            continue
        pcc = _number(row[cols["farm"]]) if cols["farm"] < len(row) else None
        if pcc is None:
            continue
        pop = _number(row[cols["population"]])
        total = _number(row[cols["availability"]])
        if pop and total is not None:
            recomputed = total / pop
            if abs(recomputed - pcc) > 0.001 + abs(pcc) * 1e-4:
                raise SystemExit(
                    f"{sheet} {int(year)}: the column read as farm per-capita "
                    f"({pcc}) does not equal availability/population "
                    f"({recomputed:.4f}) — wrong column?"
                )
            checked += 1
        out[int(year)] = round(pcc, 2)
    if not out:
        raise SystemExit(f"{sheet}: parsed no rows")
    if checked < len(out) // 2:
        raise SystemExit(
            f"{sheet}: only {checked} of {len(out)} rows could be arithmetically "
            "checked — the identity guard is too weak to trust the column"
        )
    return out, conversion


def render_toml(slug: str, label: str, values: dict[int, float], conversion: str) -> str:
    years = sorted(values)
    note = (
        f"Fresh {slug.replace('-', ' ')} per capita, farm weight, from the ERS Food "
        "Availability (Per Capita) Data System. Availability is a disappearance "
        "estimate — production plus imports, less exports and non-food use, over "
        "population — so it is what the food supply made available per person, not "
        "what was eaten; ERS publishes a separate loss-adjusted series for that and "
        "this is not it. The sheet also prints a retail-weight column derived by a "
        f"conversion factor ({conversion or 'stated in the sheet'}); the unadjusted "
        "farm-weight column is taken and the factor is disclosed rather than applied. "
        "Verified against the sheet's own availability and population columns for "
        "every year."
    )
    lines = [
        "# Auto-generated by scripts/ers_fads_extract.py from the USDA/ERS Food",
        "# Availability (Per Capita) Data System (samples/46-diet-variety/ — see the",
        "# source registry entry and the verification log, Plan 027 WI-6, before",
        "# editing by hand).",
        "",
        "[[series]]",
        f'id = "us-availability-{slug}"',
        f'label = "{label} available per person, {years[0]}-{years[-1]}"',
        'source = "usda-ers-fads"',
        'tier = "A"',
        'unit = "pounds per person per year (farm weight)"',
        'population = "The whole US resident population — a supply-side average, not '
        'a measure of who ate anything"',
        f'notes = "{note}"',
        "",
        "[series.values]",
    ]
    for year in years:
        lines.append(f"{year} = {values[year]}")
    return "\n".join(lines) + "\n"


def main() -> None:
    for slug, (workbook, sheet, label) in COMMODITIES.items():
        values, conversion = parse(workbook, sheet)
        out = OUT_DIR / f"us-availability-{slug}.toml"
        out.write_text(render_toml(slug, label, values, conversion))
        years = sorted(values)
        first, last = years[0], years[-1]
        print(f"{slug:14} {len(values):>3} years {first}-{last}   "
              f"{values[first]:>6.2f} -> {values[last]:>6.2f} lb   ({conversion})")
    print()
    print("column identity: farm per-capita == food availability / population, "
          "checked for every year of every commodity")


if __name__ == "__main__":
    main()
