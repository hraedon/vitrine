"""Read selected literal fields from inspected original XLS workbooks.

Curator-only dependencies: xlrd and openpyxl (the latter for the existing
UK ASHE helper). Install them in the research environment, not the core.
The JSON is an extraction artifact: original-byte pins, original headings,
years, units and cell addresses accompany each field. Archive-backed tests
re-extract the originals; this file is not an independent publisher source.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import struct
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PINS = {
    "36-jp-income/fies-a18-1.xls":
        "35159f6fa73f09e786857f9aee43800f880a57126a0ec09c821b0d423cdbe172",
    "36-jp-income/fies-a18-2.xls":
        "36407a833d72c661aaef7ca541405e16f5497b2624358a6a02f7a2ca8888379d",
    "36-jp-income/fies-18-02-a.xls":
        "91ea0aec3fee6b088a7297fb378bc00222535b0d5a8957d472bb2857734fd95d",
    "32-uk-housing/ons-hpi-annual-tables.xls":
        "73d680bc718472953d7e09a0b6e4640777e70981aa6dbca7293ecabb499d1c9d",
    "43-uk-hours/ashe-table1/ashe-table1-1997-table-1.zip":
        "69a084baf07231e3da3afd369068e651abb8df3ed444680111765ddf43d967c8",
    "43-uk-hours/ashe-table1/ashe-table1-2000-table-1.zip":
        "0b393f2c122068240fa40cc58629eb87ca7814f86047ae8ca8d70c505795f7c7",
    "43-uk-hours/ashe-table1/ashe-table1-2010-revised-table-1.zip":
        "48af5787fa49f8f00e757b6e4bac04fc95cd1d331a9f9a66250ac883bee4e497",
}


def norm(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def formula_cells(stream: bytes) -> frozenset[tuple[int, int]]:
    """Conservatively reject a coordinate used by a formula in any sheet.

    xlrd exposes cached formula results as numbers. BIFF FORMULA records
    must therefore be checked separately. The union across sheets may reject
    an unrelated same-coordinate formula, but cannot silently accept one.
    """
    cells: set[tuple[int, int]] = set()
    position = 0
    while position < len(stream):
        if len(stream) - position < 4:
            if any(stream[position:]):
                raise ValueError("truncated BIFF record header")
            break
        opcode, length = struct.unpack_from("<HH", stream, position)
        position += 4
        if position + length > len(stream):
            raise ValueError("truncated BIFF record")
        if opcode in {0x0006, 0x0206, 0x0406}:
            if length < 4:
                raise ValueError("truncated BIFF formula")
            cells.add(struct.unpack_from("<HH", stream, position))
        position += length
    return frozenset(cells)


class LiteralBook:
    def __init__(self, blob: bytes) -> None:
        import xlrd
        from xlrd.compdoc import CompDoc

        compound = CompDoc(blob)
        stream = compound.get_named_stream("Workbook") or compound.get_named_stream("Book")
        if not stream:
            raise ValueError("no BIFF workbook stream")
        self.formulas = formula_cells(stream)
        self.book = xlrd.open_workbook(file_contents=blob)

    def cell(self, sheet: str, row: int, column: int) -> str | int | float:
        if (row - 1, column - 1) in self.formulas:
            raise ValueError(f"formula coordinate is not a literal datum: {sheet}!R{row}C{column}")
        import xlrd

        cell = self.book.sheet_by_name(sheet).cell(row - 1, column - 1)
        if cell.ctype in {xlrd.XL_CELL_ERROR, xlrd.XL_CELL_BOOLEAN, xlrd.XL_CELL_DATE}:
            raise ValueError("unexpected source cell type")
        if cell.ctype == xlrd.XL_CELL_NUMBER:
            value = float(cell.value)
            return int(value) if value.is_integer() else value
        return norm(cell.value)


def extract(samples: Path) -> dict[str, object]:
    from uk_ashe_extract import _member

    blobs: dict[str, bytes] = {}
    for name, expected in PINS.items():
        blob = (samples / name).read_bytes()
        if hashlib.sha256(blob).hexdigest() != expected:
            raise ValueError(f"original source bytes changed: {name}")
        blobs[name] = blob

    fies: dict[str, object] = {}
    for year in (1955, 1965, 1975, 1985, 1995, 2005, 2015):
        measures: dict[str, object] = {}
        for kind in ("income", "consumption", "food"):
            if year == 1955 and kind != "income":
                continue
            early = year == 1955
            name = "36-jp-income/" + (
                "fies-18-02-a.xls" if early else
                "fies-a18-2.xls" if kind == "income" else "fies-a18-1.xls"
            )
            book = LiteralBook(blobs[name])
            sheet = book.book.sheet_names()[0]
            rows = [
                row for row in range(1, book.book.sheet_by_name(sheet).nrows + 1)
                if book.cell(sheet, row, 2) == year
            ]
            if len(rows) != 1:
                raise ValueError(f"expected one source year: {name}, {year}")
            row = rows[0]
            column = 6 if early else 8 if kind in {"income", "food"} else 7
            header = (9, 6) if early else (5, 8) if kind == "income" else (
                (7, 8) if kind == "food" else (5, 7)
            )
            measures[kind] = {
                "value": book.cell(sheet, row, column),
                "year": str(book.cell(sheet, row, 2)),
                "title": book.cell(sheet, 2, 1),
                "heading": book.cell(sheet, *header),
                "unit": book.cell(sheet, 3, 3) if early else book.cell(sheet, 11, 7),
                "exclusion": "" if early else book.cell(
                    sheet, 81 if kind == "income" else 82, 3,
                ),
                "file": name,
                "sha256": PINS[name],
                "cell": f"{sheet}!R{row}C{column}",
            }
        fies[str(year)] = measures

    name = "32-uk-housing/ons-hpi-annual-tables.xls"
    book = LiteralBook(blobs[name])
    sheet = "Table 31"
    housing: dict[str, object] = {}
    for year in (1997, 2000, 2010):
        rows = [
            r for r in range(1, book.book.sheet_by_name(sheet).nrows + 1)
            if book.cell(sheet, r, 1) == year
        ]
        if len(rows) != 1:
            raise ValueError("house-price year is missing or duplicated")
        row = rows[0]
        housing[str(year)] = {
            "value": book.cell(sheet, row, 2), "year": str(year),
            "title": book.cell(sheet, 1, 1), "heading": book.cell(sheet, 3, 2),
            "sha256": PINS[name], "cell": f"{sheet}!R{row}C2",
        }

    ashe: dict[str, object] = {}
    for year in (1997, 2000, 2010):
        name = next(n for n in PINS if f"ashe-table1-{year}-" in n)
        values: dict[str, object] = {}
        with zipfile.ZipFile(io.BytesIO(blobs[name])) as archive:
            for kind, table in (("hourly", "1.5a"), ("hours", "1.9a")):
                member = _member(archive, table)
                blob = archive.read(member)
                book = LiteralBook(blob)
                sheet = "All"
                grid = book.book.sheet_by_name(sheet)
                headers = [
                    (r, c) for r in range(1, grid.nrows + 1)
                    for c in range(1, grid.ncols + 1)
                    if norm(book.cell(sheet, r, c)).lower() == "median"
                ]
                rows = [
                    r for r in range(1, grid.nrows + 1)
                    if norm(book.cell(sheet, r, 1)).lower() == "all employees"
                ]
                if len(headers) != 1 or len(rows) != 1:
                    raise ValueError("ASHE median header or employee row is ambiguous")
                header_row, column = headers[0]
                values[kind] = {
                    "value": book.cell(sheet, rows[0], column),
                    "year": str(year), "title": book.cell(sheet, 1, 1),
                    "heading": book.cell(sheet, header_row, column),
                    "population": book.cell(sheet, rows[0], 1), "sheet": sheet,
                    "archive_sha256": PINS[name],
                    "member": member, "member_sha256": hashlib.sha256(blob).hexdigest(),
                    "cell": f"{sheet}!R{rows[0]}C{column}",
                }
        ashe[str(year)] = values
    return {"fies": fies, "housing": housing, "ashe": ashe}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=REPO / "samples")
    args = parser.parse_args()
    result = extract(args.samples)
    destination = args.samples / "59-workbook-review" / "observations.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n",
    )
    print(f"Re-extracted selected original workbook fields to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
