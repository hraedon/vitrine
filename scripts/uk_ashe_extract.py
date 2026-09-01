#!/usr/bin/env python3
"""Extract the UK hourly-pay and paid-hours anchors from ONS ASHE Table 1.

Source: ``samples/43-uk-hours/ashe-table1/`` — one zip per published year,
1997 through 2025 provisional. Each zip holds the Table 1 workbooks; this
script reads two of them:

- ``1.5a  Hourly pay - Gross``      — £ per hour, median and mean
- ``1.9a  Paid hours worked - Total`` — hours per week, median and mean

Both are read from the ``All`` sheet (all employee jobs, both sexes, full- and
part-time) on the ``All Employees`` row, which is the population ASHE headlines.
The ``Full-Time`` sheet is printed alongside as context, because a median over
all employees includes part-timers and sits well below the full-time median —
a reader who assumes "the wage" means full-time would be misled by the number
alone.

The survey covers employees on adult rates whose pay in the survey pay-period
was not affected by absence, sampled at April from a 1% sample of National
Insurance numbers.

Traps this script exists to defeat:

1. **The workbooks change format and name mid-series.** 1997-2010 are ``.xls``
   (read with xlrd), later years ``.xlsx`` (openpyxl); the member names gain
   and lose ``REVISED - All Employees`` prefixes and double spaces. Members are
   therefore located by a normalised table-number match, not by file name.
2. **The header row moves.** The value row is found by its ``All Employees``
   label with the column offsets read from the ``Median``/``Mean`` header cells,
   never by fixed indices.
3. Every value is printed with the workbook member and sheet it came from, so a
   transcription can be re-derived rather than trusted.

Usage: ``python scripts/uk_ashe_extract.py [year ...]`` (default: the UK rooms'
decade-anchor years).
"""

from __future__ import annotations

import io
import re
import sys
import zipfile
from pathlib import Path

import openpyxl
import xlrd

REPO = Path(__file__).resolve().parent.parent
ASHE = REPO / "samples" / "43-uk-hours" / "ashe-table1"

# year -> the zip to read. Where ONS published both a provisional and a revised
# edition of a year, the revised one is used and named here explicitly.
ZIP_FOR_YEAR = {
    1997: "ashe-table1-1997-table-1.zip",
    2000: "ashe-table1-2000-table-1.zip",
    2010: "ashe-table1-2010-revised-table-1.zip",
}
DEFAULT_YEARS = (1997, 2000, 2010)

TABLES = {"1.5a": "Hourly pay - Gross (£/hour)", "1.9a": "Paid hours worked - Total (hours/week)"}
SHEETS = ("All", "Full-Time")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _member(zf: zipfile.ZipFile, table: str) -> str:
    """The workbook in this zip for a table number, e.g. '1.5a'."""
    # 2000-2003 zips drop the word "Table" from the member name and 2010 adds a
    # "REVISED - " prefix, so match the table number itself, bounded so that
    # "1.1a" cannot match inside "1.11a".
    wanted = re.compile(rf"(?<![\d.]){re.escape(table)}(?![\da-z])")
    hits = [n for n in zf.namelist() if wanted.search(_norm(n).lower()) and not n.startswith("__")]
    if len(hits) != 1:
        raise SystemExit(f"table {table}: expected one member, got {hits}")
    return hits[0]


def _grid(data: bytes, member: str, sheet: str) -> list[list[object]]:
    """The sheet as a row-major grid, whichever workbook format it is."""
    if member.lower().endswith(".xls"):
        book = xlrd.open_workbook(file_contents=data)
        sh = book.sheet_by_name(sheet)
        return [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
    book_x = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    try:
        return [list(r) for r in book_x[sheet].iter_rows(values_only=True)]
    finally:
        book_x.close()


def read_table(zf: zipfile.ZipFile, table: str, sheet: str) -> dict[str, object]:
    """The All-Employees row of one ASHE table, located by its header labels."""
    member = _member(zf, table)
    grid = _grid(zf.read(member), member, sheet)

    header_row = next(
        (i for i, row in enumerate(grid) if any(_norm(c).lower() == "median" for c in row)),
        None,
    )
    if header_row is None:
        raise SystemExit(f"{member} [{sheet}]: no header row carrying 'Median'")
    cols = {
        _norm(c).lower(): i
        for i, c in enumerate(grid[header_row])
        if _norm(c).lower() in {"median", "mean", "number of jobs", "code", "description"}
    }
    # 'Number of jobs' is stacked over two header rows ('Number' / 'of jobs').
    if "number of jobs" not in cols:
        for i, c in enumerate(grid[header_row]):
            if _norm(c).lower() == "number":
                cols["number of jobs"] = i
        for i, c in enumerate(grid[max(header_row - 2, 0)]):
            if _norm(c).lower() == "number":
                cols["number of jobs"] = i

    value_row = next(
        (i for i, row in enumerate(grid) if row and _norm(row[0]).lower() == "all employees"),
        None,
    )
    if value_row is None:
        raise SystemExit(f"{member} [{sheet}]: no 'All Employees' row")

    row = grid[value_row]
    out: dict[str, object] = {"member": member, "sheet": sheet, "title": _norm(grid[0][0])}
    for key in ("number of jobs", "median", "mean"):
        idx = cols.get(key)
        out[key] = row[idx] if idx is not None and idx < len(row) else None
    return out


def main(argv: list[str]) -> int:
    years = [int(a) for a in argv[1:]] or list(DEFAULT_YEARS)
    for year in years:
        name = ZIP_FOR_YEAR.get(year)
        if name is None:
            raise SystemExit(f"no zip registered for {year}; add it to ZIP_FOR_YEAR")
        print(f"\n=== ASHE {year} — {name} ===")
        with zipfile.ZipFile(ASHE / name) as zf:
            for table, what in TABLES.items():
                print(f"  -- table {table}: {what}")
                for sheet in SHEETS:
                    got = read_table(zf, table, sheet)
                    print(f"     [{sheet:9s}] median={got['median']!r} mean={got['mean']!r} "
                          f"jobs(thousand)={got['number of jobs']!r}")
                    print(f"        from {got['member']!r}")
                    print(f"        titled {got['title']!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
