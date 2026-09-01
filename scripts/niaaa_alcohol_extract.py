#!/usr/bin/env python3
"""Extract the Plan 027 WI-3 alcohol series from the archived primary table.

Emits ``data/series/us-ethanol-per-capita.toml`` from Table 1 of NIAAA
Surveillance Report #122 (``samples/34-smoking/niaaa-surveillance-122.pdf``,
never committed; the archive is the transcription source).

The table is read out of the PDF itself, not out of the flattened text dump
beside it and not out of the markdown extraction summary in the same
directory -- a summary is a secondary source, and the museum's truth-path rule
is that values are transcribed from the document. The PDF's text layer emits
Table 1 as one token per line, ``YEAR ......`` followed by the Beer, Wine,
Spirits and All-beverages columns in that order; this script reads the
all-beverages column only and asserts the row shape, so a layout change is a
loud failure rather than a silent misparse.

Three properties of the table survive into the data and must not be smoothed
away (Plan 027 D2):

  * **Prohibition prints as a gap.** Between the 1934 row and the 1916-1919
    row the table prints the literal word ``(Prohibition)`` and no numbers.
    The series therefore begins at 1934. Nothing is interpolated across
    1920-1933; the absence is the exhibit.
  * **Pre-1934 data is grouped, not annual.** The early record is published as
    multi-year ranges (1896-1900, 1906-1910, ...), plus three isolated single
    years 1850, 1860 and 1870. A range is not a year, so none of the ranges
    can enter a year-keyed series without inventing a datum. The three early
    single years could, but putting them in would draw one line from 1850 to
    2023 across a 63-year void that is really two different absences -- a
    grouped-publication era and a measurement collapse -- and they sit before
    the museum's 1890s floor besides. The series is therefore the continuous
    annual record, 1934-2023. Everything excluded is printed for transcription
    into the decade rooms' facts, where a range can be named in the value.
  * **The population basis changes.** The table header reads "based on
    population ages 15 and older prior to 1970 and on population ages 14 and
    older thereafter", so 1970 onward is the 14+ basis. This is carried in the
    series notes, not corrected for.

Provenance: the table's own note says "Data prior to 1977 are from Hyman et
al. 1980" -- the pre-1977 half of an official series is republished scholarly
work. That is disclosed in the series notes and is why the arc carries a
caveat rather than a silent tier-A claim across the whole span.

Spot-verification (see docs/verification-log.md, Plan 027 WI-3): every parsed
row is printed at the end; the operator compares them against the PDF.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PDF = REPO / "samples" / "34-smoking" / "niaaa-surveillance-122.pdf"
OUT = REPO / "data" / "series" / "us-ethanol-per-capita.toml"

# "1970 ......................" or "1896–1900 ............" (en dash in the PDF)
ROW_LABEL = re.compile(r"^(\d{4}(?:[–-]\d{4})?)\s*\.{3,}$")
NUMBER = re.compile(r"^\d+\.\d{2}$")

TABLE_TITLE = "Apparent per capita ethanol consumption, United States, 1850"
PROHIBITION = "(Prohibition)"


def _table_pages(doc: object) -> list[str]:
    """The Table 1 pages, in document order (the table runs over two pages)."""
    pages = []
    for page in doc:  # type: ignore[attr-defined]
        text = page.get_text()
        # The contents page names the table and carries its own dot leader, so
        # presence of the title is not enough; a real table page is dense with
        # row labels.
        if TABLE_TITLE not in text:
            continue
        rows = sum(1 for line in text.splitlines() if ROW_LABEL.match(line.strip()))
        if rows >= 20:
            pages.append(text)
    return pages


SERIES_FLOOR = 1934  # the first year of the continuous post-Repeal record


COLUMNS = ("beer", "wine", "spirits", "all")


def parse_table_one() -> tuple[dict[int, float], dict[str, float], bool]:
    """Return (single-year all-beverage values, grouped ranges, prohibition seen).

    ``parse_table_columns`` exposes all four columns for cross-checks; this
    function keeps the all-beverages column, which is what the series carries.
    """
    single, grouped, seen = parse_table_columns()
    return (
        {y: row["all"] for y, row in single.items()},
        {k: row["all"] for k, row in grouped.items()},
        seen,
    )


def parse_table_columns() -> tuple[
    dict[int, dict[str, float]], dict[str, dict[str, float]], bool
]:
    """Return every published cell of Table 1, keyed by year/range then column."""
    import fitz  # PyMuPDF; dev-only dependency of this script

    doc = fitz.open(PDF)
    pages = _table_pages(doc)
    if len(pages) != 2:
        raise SystemExit(f"expected Table 1 to span 2 pages, found {len(pages)}")

    tokens = [line.strip() for page in pages for line in page.splitlines()]
    tokens = [t for t in tokens if t]

    annual: dict[int, dict[str, float]] = {}
    grouped: dict[str, dict[str, float]] = {}
    prohibition_seen = False

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == PROHIBITION:
            prohibition_seen = True
            i += 1
            continue
        match = ROW_LABEL.match(token)
        if match is None:
            i += 1
            continue
        cells = tokens[i + 1 : i + 5]
        if len(cells) != 4 or not all(NUMBER.match(c) for c in cells):
            raise SystemExit(
                f"row {token!r} is not followed by four numeric cells: {cells!r}"
            )
        row = dict(zip(COLUMNS, (float(c) for c in cells), strict=True))
        label = match.group(1)
        if "–" in label or "-" in label:
            grouped[label] = row
        else:
            year = int(label)
            if year in annual:
                raise SystemExit(f"year {year} appears twice in Table 1")
            annual[year] = row
        i += 5

    return annual, grouped, prohibition_seen


def render_toml(annual: dict[int, float]) -> str:
    lines = [
        "# Auto-generated by scripts/niaaa_alcohol_extract.py from NIAAA",
        "# Surveillance Report #122, Table 1 (samples/34-smoking/ — see the source",
        "# registry entry and the verification log, Plan 027 WI-3, before editing",
        "# by hand).",
        "",
        "[[series]]",
        'id = "us-ethanol-per-capita"',
        'label = "Apparent per capita ethanol consumption, all beverages, 1934-2023"',
        'source = "niaaa-surveillance-122"',
        'tier = "A"',
        'unit = "gallons of pure ethanol per person per year"',
        'population = "U.S. population ages 15 and older before 1970; ages 14 and '
        'older from 1970 onward"',
        "notes = \"Table 1, all-beverages column. Apparent consumption: derived from "
        "legal beverage sales and shipments, so it measures what the state could "
        "count, not what was drunk. The series begins at 1934 because the table "
        "prints '(Prohibition)' and no values for 1920-1933 — the gap is the "
        "exhibit and is not interpolated. Pre-1934 figures are published as "
        "multi-year ranges rather than single years and so cannot enter a "
        "year-keyed series; they are carried as decade facts instead. The "
        "population basis changes at 1970 (15+ before, 14+ from). The table's own "
        "note records that data prior to 1977 are from Hyman et al. 1980.\"",
        "",
        "[series.values]",
    ]
    for year in sorted(annual):
        lines.append(f"{year} = {annual[year]:.2f}")
    return "\n".join(lines) + "\n"


def main() -> None:
    single, grouped, prohibition_seen = parse_table_one()

    if not prohibition_seen:
        raise SystemExit(
            "the literal '(Prohibition)' row was not found — the table layout "
            "changed, and the gap this series exists to render is unverified"
        )
    straddling = sorted(y for y in single if 1920 <= y <= 1933)
    if straddling:
        raise SystemExit(f"Prohibition years carry values: {straddling}")

    annual = {y: v for y, v in single.items() if y >= SERIES_FLOOR}
    early = {y: v for y, v in single.items() if y < SERIES_FLOOR}
    if min(annual) != SERIES_FLOOR:
        raise SystemExit(f"expected the series to start at {SERIES_FLOOR}, got {min(annual)}")
    if sorted(annual) != list(range(min(annual), max(annual) + 1)):
        missing = sorted(set(range(min(annual), max(annual) + 1)) - set(annual))
        raise SystemExit(f"the post-Repeal record is not continuous; missing {missing}")

    OUT.write_text(render_toml(annual))

    print(f"wrote {OUT.relative_to(REPO)}: {len(annual)} annual values "
          f"{min(annual)}-{max(annual)}, continuous")
    print()
    print("== in the series: annual, all beverages, gallons of ethanol per capita ==")
    for year in sorted(annual):
        print(f"  {year}  {annual[year]:.2f}")
    print()
    print("== NOT in the series: grouped ranges (transcribe as decade facts) ==")
    for label in grouped:
        print(f"  {label}  {grouped[label]:.2f}")
    print()
    print("== NOT in the series: isolated early single years (before the museum floor) ==")
    for year in sorted(early):
        print(f"  {year}  {early[year]:.2f}")
    print()
    print("== the gap ==")
    print("  1920-1933  (Prohibition) — printed by the table, no values")
    print()
    print("== decade anchors (the room facts transcribe these) ==")
    for decade, key in DECADE_ANCHORS:
        if key is None:
            print(f"  {decade}  GAP — national Prohibition")
            continue
        if isinstance(key, int):
            value = single[key]
            print(f"  {decade}  {value:.2f}   (single year {key})")
        else:
            value = grouped[key]
            print(f"  {decade}  {value:.2f}   (published range {key})")


# One anchor per room. Single years are the decade's first published year, the
# convention the cigarette facts already use. The 1900s and 1910s have no
# single-year figure at all -- the table publishes five-year ranges there -- so
# each room takes the range that lies wholly inside its own decade (1896-1900
# and 1906-1910 both straddle a boundary and would put a neighbour's years on
# the card). The 1920s is the gap. The 1930s cannot start at 1930: the decade
# opens inside Prohibition, so its first published year is 1934.
DECADE_ANCHORS: tuple[tuple[str, int | str | None], ...] = (
    ("1900s", "1901–1905"),
    ("1910s", "1911–1915"),
    ("1920s", None),
    ("1930s", 1934),
    ("1940s", 1940),
    ("1950s", 1950),
    ("1960s", 1960),
    ("1970s", 1970),
    ("1980s", 1980),
    ("1990s", 1990),
    ("2000s", 2000),
    ("2010s", 2010),
    ("2020s", 2020),
)


if __name__ == "__main__":
    main()
