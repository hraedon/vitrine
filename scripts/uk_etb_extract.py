#!/usr/bin/env python3
"""Extract the UK household income anchor from the ONS ETB household-type tables.

Source: ``samples/30-uk-income/etb-hhldtype.xlsx`` — ONS "Effects of taxes and
benefits on household income", historical dataset, summary by household type.
One sheet per financial year, 1977 through FYE 2017/18, in **nominal** (current)
prices, averages per household, £ per year.

The column this project wants is the non-retired ``2 adults with 2 children``
household: the closest official UK counterpart to the museum's composite
four-person family. Its ``Disposable income`` row is the income anchor
(post-cash-benefit, post-direct-tax, pre-indirect-tax), and is transcribed as-is
— nominal, no deflation, no equivalisation.

Two traps this script exists to defeat:

1. **The column moves.** The 1977-1980s sheets carry a different header block
   from 1990 onward (an extra ``1 adult Men/Women`` split appears), so a fixed
   column index silently reads "2 adults with 1 child" for half the series.
   The target column is therefore located by *composing* the stacked header
   cells and matching the composed text, never by position.
2. **A silent match is not evidence.** The script prints the composed header of
   every column in the non-retired block, marks the one it picked, and prints
   the neighbouring columns' values, so a wrong column is visible rather than
   merely absent. See docs/verification-log.md.

Usage: ``python scripts/uk_etb_extract.py [sheet ...]`` (default: the anchor
years used by the UK rooms).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parent.parent
BOOK = REPO / "samples" / "30-uk-income" / "etb-hhldtype.xlsx"

# The decade-anchor sheets the UK rooms cite.
DEFAULT_SHEETS = ("1977", "1980", "1990", "2000-01", "2010-11")

TARGET = "2 adults with 2 children"
ROWS_WANTED = (
    "Original income",
    "Cash benefits",
    "Gross income",
    "Direct taxes and employees' NIC",
    "Disposable income",
    "Equivalised disposable income",
)


def _norm(text: str) -> str:
    """Header text with footnote digits and whitespace runs removed."""
    text = re.sub(r"(?<=[a-z])\d+\b", "", text)  # 'adults2' -> 'adults'
    return re.sub(r"\s+", " ", text).strip().lower()


def _row_label(cell: object) -> str:
    """Row label with its ``plus``/``less`` prefix and footnote digits removed.

    ``Equivalised4 disposable income`` and ``Equivalised disposable3 income``
    both occur in this workbook; a label match that does not strip the footnote
    marker drops the row silently, which reads exactly like the row not existing.
    """
    text = re.sub(r"\s+", " ", str(cell or "")).strip()
    text = re.sub(r"^(plus|less)\s+", "", text, flags=re.I)
    return re.sub(r"(?<=[A-Za-z])\d+(?=\b|\s)", "", text).strip()


def block_bounds(rows: list[tuple[object, ...]]) -> tuple[int, int]:
    """First and last row index of the non-retired household-type block."""
    start = end = -1
    for i, row in enumerate(rows):
        joined = " ".join(str(c) for c in row if c is not None)
        if start < 0 and "Non-Retired" in joined:
            start = i
        elif start >= 0 and joined.strip().startswith("Average per household"):
            end = i
            break
    if start < 0 or end < 0:
        raise SystemExit("could not locate the non-retired block")
    return start, end


def composed_headers(rows: list[tuple[object, ...]], start: int, end: int) -> dict[int, str]:
    """Column index -> its header, composed down the stacked header rows."""
    width = max(len(r) for r in rows[start:end])
    headers: dict[int, str] = {}
    for col in range(1, width):
        parts = [
            str(rows[r][col]).strip()
            for r in range(start, end)
            if col < len(rows[r]) and rows[r][col] is not None and str(rows[r][col]).strip()
        ]
        if parts:
            headers[col] = _norm(" ".join(parts))
    return headers


def read_sheet(book: openpyxl.Workbook, sheet: str) -> None:
    rows = [tuple(r) for r in book[sheet].iter_rows(values_only=True)]
    start, end = block_bounds(rows)
    headers = composed_headers(rows, start, end)

    picked = [c for c, h in headers.items() if h == TARGET]
    print(f"\n=== sheet {sheet} — non-retired block, header rows {start}..{end - 1} ===")
    for col in sorted(headers):
        mark = "  <== ANCHOR COLUMN" if col in picked else ""
        print(f"  col {col:2d}: {headers[col]!r}{mark}")
    if len(picked) != 1:
        raise SystemExit(f"sheet {sheet}: expected exactly one {TARGET!r} column, got {picked}")
    col = picked[0]

    print(f"  --- values (£ per year, nominal), sheet {sheet} ---")
    for i in range(end, len(rows)):
        label = _row_label(rows[i][0] if rows[i] else "")
        if label in ROWS_WANTED:
            neighbours = {
                headers[c]: rows[i][c]
                for c in sorted(headers)
                if c != col and c < len(rows[i]) and rows[i][c] is not None
            }
            value = rows[i][col] if col < len(rows[i]) else None
            print(f"  {label:32s} {value!r}")
            print(f"      others: {neighbours}")


def main(argv: list[str]) -> int:
    sheets = argv[1:] or list(DEFAULT_SHEETS)
    book = openpyxl.load_workbook(BOOK, read_only=True, data_only=True)
    try:
        for sheet in sheets:
            read_sheet(book, sheet)
    finally:
        book.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
