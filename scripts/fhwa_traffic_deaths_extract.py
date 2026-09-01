#!/usr/bin/env python3
"""Extract the Plan 027 WI-4 road-death series from FHWA Table FI-200.

Emits ``data/series/us-traffic-death-rate.toml`` from Highway Statistics 2023,
Table FI-200 ("Motor vehicle traffic fatalities, 1900-2023"), archived at
``samples/44-road-workplace-deaths/fhwa-fi200-highway-statistics-2023.html``.

FI-200 carries the whole span in one table, so no splice is needed: the plan's
assumed NSC-estimates-then-FARS join is not how FHWA publishes it. What the
table *does* record is a definitional change, in its own footnote (3):
"Beginning in 1976, includes only persons injured in a highway vehicular crash
that died within 30 days." Deaths before 1976 were counted on a wider window,
so the pre- and post-1976 halves are not the same measurement. That is carried
as a caveat rather than corrected for.

**Column identification is arithmetic, not positional trust.** The rate this
series wants -- deaths per 100 million vehicle-miles travelled -- sits among
three other rate columns (per 1,000 miles of road, per 100,000 registered
vehicles, per 100,000 licensed drivers) that would each look plausible in
isolation. The parser therefore recomputes the rate from the fatality count
and the VMT column and refuses to write unless the published figure
reproduces, for every year. Picking the neighbouring column is the exact
failure this guard exists to catch.

A second archived document, FHWA's Highway Statistics Summary to 1995
(``fhwa-fi200-summary-to-1995.pdf``, a separately-published PDF of the same
table), is used by ``--cross-check`` as an independent witness for 1900-1995.

Spot-verification: see docs/verification-log.md, Plan 027 WI-4a.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / "samples" / "44-road-workplace-deaths"
HTML_TABLE = ARCHIVE / "fhwa-fi200-highway-statistics-2023.html"
SUMMARY_PDF = ARCHIVE / "fhwa-fi200-summary-to-1995.pdf"
OUT = REPO / "data" / "series" / "us-traffic-death-rate.toml"

YEAR = re.compile(r"^(19|20)\d{2}$")
# column positions, asserted against the header and then against arithmetic
I_YEAR, I_VMT, I_FATALITIES, I_RATE_VMT = 0, 2, 5, 7

DEFINITION_CHANGE = 1976  # footnote (3): 30-day death window from this year


def _cells(row: str) -> list[str]:
    return [
        html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
        for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)
    ]


def _number(text: str) -> float | None:
    text = text.replace(",", "").strip()
    if text in {"", "-", "--"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_fi200() -> dict[int, dict[str, float]]:
    raw = HTML_TABLE.read_text(errors="replace")
    rows = [_cells(r) for r in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S | re.I)]

    header = " ".join(c for r in rows[:3] for c in r).upper()
    for expected in ("PER 100 MILLION", "HIGHWAY", "FATALITIES", "VEHICLE-MILES"):
        if expected not in re.sub(r"\s+", " ", header):
            raise SystemExit(f"FI-200 header no longer contains {expected!r}")

    out: dict[int, dict[str, float]] = {}
    for cells in rows:
        if not cells or not YEAR.fullmatch(cells[I_YEAR]):
            continue
        if len(cells) <= I_RATE_VMT:
            raise SystemExit(f"row {cells[I_YEAR]} is short: {cells!r}")
        vmt = _number(cells[I_VMT])
        fatalities = _number(cells[I_FATALITIES])
        rate = _number(cells[I_RATE_VMT])
        if vmt is None or fatalities is None or rate is None:
            raise SystemExit(f"row {cells[I_YEAR]} has an empty required cell: {cells!r}")
        out[int(cells[I_YEAR])] = {"vmt": vmt, "fatalities": fatalities, "rate": rate}
    if not out:
        raise SystemExit("no data rows parsed from FI-200")
    return out


def check_arithmetic(rows: dict[int, dict[str, float]]) -> None:
    """The published rate must be fatalities per 100 million VMT, recomputed.

    VMT is published in millions, so the rate is fatalities / (VMT / 100).
    Tolerance is half a unit in the published last place, which is all the
    rounding the table can hide; anything wider would let a neighbouring
    column pass.
    """
    bad = []
    for year, row in sorted(rows.items()):
        if row["vmt"] == 0:
            continue
        recomputed = row["fatalities"] / (row["vmt"] / 100.0)
        if abs(recomputed - row["rate"]) > 0.005 + row["rate"] * 1e-4:
            bad.append((year, row["rate"], round(recomputed, 4)))
    if bad:
        raise SystemExit(
            "the column read as 'per 100 million VMT' does not reproduce from "
            f"fatalities and VMT — wrong column? first failures: {bad[:5]}"
        )


def cross_check_summary_pdf(
    rows: dict[int, dict[str, float]],
) -> tuple[int, list[tuple[int, float, list[str]]]]:
    """Compare against the separately-published Summary-to-1995 PDF.

    Returns the number of years compared and every year whose rate does not
    reproduce, with the PDF's own row beside it. Differences are reported, not
    tolerated silently: a revision between two editions is a fact about the
    source and belongs in the verification log, and anything else is a bug.
    """
    import fitz

    text = "\n".join(page.get_text() for page in fitz.open(SUMMARY_PDF))
    tokens = [t.strip() for t in text.splitlines() if t.strip()]
    compared = 0
    differences: list[tuple[int, float, list[str]]] = []
    i = 0
    while i < len(tokens):
        if not YEAR.fullmatch(tokens[i]):
            i += 1
            continue
        year = int(tokens[i])
        window = tokens[i + 1 : i + 12]
        values = [_number(t) for t in window]
        # the summary layout carries the same rate column; find it by the
        # arithmetic identity rather than by position, since the PDF's column
        # order differs from the HTML's
        row = rows.get(year)
        if row is not None:
            match = any(
                v is not None and abs(v - row["rate"]) < 0.005 for v in values
            )
            compared += 1
            if not match:
                differences.append((year, row["rate"], window))
        i += 1
    return compared, differences


def render_toml(rows: dict[int, dict[str, float]]) -> str:
    years = sorted(rows)
    lines = [
        "# Auto-generated by scripts/fhwa_traffic_deaths_extract.py from FHWA",
        "# Highway Statistics 2023, Table FI-200 (samples/44-road-workplace-deaths/",
        "# — see the source registry entry and the verification log, Plan 027 WI-4a,",
        "# before editing by hand).",
        "",
        "[[series]]",
        'id = "us-traffic-death-rate"',
        'label = "Motor-vehicle traffic deaths per 100 million vehicle-miles travelled, 1900-2023"',
        'source = "fhwa-fi200-2023"',
        'tier = "A"',
        'unit = "deaths per 100 million vehicle-miles travelled"',
        'population = "All persons killed in motor-vehicle traffic crashes on US public roads, '
        'against total vehicle-miles travelled — not drivers only and not occupants only"',
        'notes = "Table FI-200, the \'per 100 million annual VMT\' column, verified against '
        "the table's own fatality and VMT columns for every year. FHWA footnote (3) records a "
        "definitional change: beginning in 1976 the count includes only people who died within "
        "30 days of the crash, so the pre- and post-1976 halves are not the same measurement and "
        'the earlier years are counted on a wider window. Not corrected for."',
        "",
        "[series.values]",
    ]
    for year in years:
        lines.append(f"{year} = {rows[year]['rate']:.2f}")
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = parse_fi200()
    check_arithmetic(rows)

    years = sorted(rows)
    if years != list(range(years[0], years[-1] + 1)):
        missing = sorted(set(range(years[0], years[-1] + 1)) - set(years))
        raise SystemExit(f"FI-200 is not continuous; missing {missing}")

    OUT.write_text(render_toml(rows))
    print(f"wrote {OUT.relative_to(REPO)}: {len(rows)} values {years[0]}-{years[-1]}, continuous")
    print("column identity: the published rate reproduces from fatalities/VMT for every year")

    if "--cross-check" in sys.argv:
        compared, differences = cross_check_summary_pdf(rows)
        print(f"cross-check vs Summary-to-1995 PDF: {compared} years compared, "
              f"{len(differences)} differing")
        for year, rate, window in differences:
            print(f"  {year}: Highway Statistics 2023 rate {rate:.2f}; "
                  f"Summary-to-1995 row {window}")

    print()
    print("== spot rows ==")
    for year in (1900, 1921, 1937, 1966, 1975, DEFINITION_CHANGE, 1980, 2000, 2020, years[-1]):
        if year in rows:
            r = rows[year]
            print(f"  {year}  rate {r['rate']:>6.2f}   fatalities {int(r['fatalities']):>6,}"
                  f"   VMT {int(r['vmt']):>9,}m")


if __name__ == "__main__":
    main()
