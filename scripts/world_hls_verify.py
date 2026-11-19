"""Check selected Japan Statistical Yearbook HLS cells against publisher XLS.

Curator utility only: requires xlrd 2.x outside the stdlib-only vitrine core.
It checks pinned publisher bytes, headings, dates, and twelve observations. It
does not write facts or audit ledger entries, and does not validate prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from workbook_review_extract import LiteralBook

FILES = {
    'jsy2016-y652101000.xls': 'a66515ed7dc3d73dc0a440e3f36c3786e720c533cc561ef2894f0fb8c0e9c0de',
    'jsy2016-y652105000.xls': '8bcf5903fa5cb9cc46985e7324eae4f77ed16b8eeac6ba1c3db4418f4cf263b7',
}
ROWS = ((11, 15, 1988, 4.86, 89.29, 61.3),
        (12, 16, 1993, 4.85, 91.92, 59.8),
        (14, 18, 2003, 4.77, 94.85, 61.2),
        (16, 20, 2013, 4.59, 94.42, 61.7))


def verify(root: Path) -> dict[str, object]:
    sheets = []
    for name, expected in FILES.items():
        path = root / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Publisher source hash differs: {path}')
        sheets.append(LiteralBook(path.read_bytes()))
    size, tenure = sheets
    size_sheet, tenure_sheet = 'y2101000', 'y2105000'
    for book, sheet, title in ((size, size_sheet, 'DWELLINGS, HOUSEHOLDS'),
                               (tenure, tenure_sheet, 'NUMBER OF DWELLINGS')):
        if (
            title not in str(book.cell(sheet, 2, 1))
            or 'Housing and Land Survey' not in str(book.cell(sheet, 5, 1))
        ):
            raise ValueError('Source title or survey heading changed')
    if (
        'Occupied dwellings' not in str(size.cell(size_sheet, 7, 10))
        or 'Ratio of owned houses' not in str(tenure.cell(tenure_sheet, 9, 10))
    ):
        raise ValueError('Population or metric heading changed')
    rows: dict[str, object] = {}
    for size_row, tenure_row, year, rooms, area, ratio in ROWS:
        actual = (size.cell(size_sheet, size_row, 2), tenure.cell(tenure_sheet, tenure_row, 2),
                  size.cell(size_sheet, size_row, 10), size.cell(size_sheet, size_row, 12),
                  tenure.cell(tenure_sheet, tenure_row, 10))
        expected = (year, year, rooms, area, ratio)
        if actual != expected:
            raise ValueError(f'{year}: expected {expected}, got {actual}')
        print(f'{year}: rooms={rooms} area_m2={area} owned_dwellings_pct={ratio}')
        rows[str(year)] = {
            'year': year,
            'rooms': {'value': actual[2], 'address': f'{size_sheet}!J{size_row}',
                      'heading': size.cell(size_sheet, 9, 10)},
            'area': {'value': actual[3], 'address': f'{size_sheet}!L{size_row}',
                     'heading': size.cell(size_sheet, 9, 12),
                     'unit': size.cell(size_sheet, 10, 12)},
            'owned': {'value': actual[4], 'address': f'{tenure_sheet}!J{tenure_row}',
                      'heading': tenure.cell(tenure_sheet, 9, 10),
                      'unit': tenure.cell(tenure_sheet, 10, 10)},
        }
    return {'kind': 'curator extraction, not an independent publisher source',
            'publisher_files_sha256': FILES, 'population': 'Occupied dwellings',
            'survey': 'Housing and Land Survey; 1 October', 'rows': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('housing_archive', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify(args.housing_archive)
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n',
                               encoding='utf-8', newline='\n')
