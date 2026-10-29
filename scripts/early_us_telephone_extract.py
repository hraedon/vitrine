"""Reproduce historical telephone instruments and rates from the Census table.

Curator-only extraction; requires pypdf. Rates count instruments and extensions
per population, not the proportion of households with a telephone.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILE = '11-historical-statistics/hstat1970_cen_1975_v2.pdf'
SHA256 = '0e209a421af0cf48af7261f6fbd7a599c27a0afce5b7523f2bc89a7d18647fa5'
YEARS = (1900, 1915, 1925, 1935, 1940, 1950, 1960, 1970)


def parse_table(text: str) -> dict[str, object]:
    header = re.sub(r'\s+', ' ', text[:800])
    for guard in ('Series R 1-12.', 'In thousands, except series R 2 and R 3',
                  'Telephones', 'Total', 'Number Per 1,000 population'):
        if guard not in header:
            raise ValueError('telephone table header or unit changed')
    rows: dict[str, dict[str, str]] = {}
    for year in YEARS:
        pattern = rf'(?m)^{year}[-._ ]*\s+([\d,]+)\s+(\d+\.\d+)\s*$'
        found = re.findall(pattern, text)
        if len(found) != 1:
            raise ValueError(f'year {year} row absent or ambiguous')
        number, rate = found[0]
        if not re.fullmatch(r'\d{1,3}(?:,\d{3})*', number):
            raise ValueError(f'year {year} number format invalid')
        rows[str(year)] = {'number_thousands': number, 'per_1000_population': rate}
    return {'source_sha256': SHA256, 'pdf_page': 191, 'series': 'R 1–12',
            'population': 'Telephone instruments and extensions per total population',
            'rows': rows}


def extract(blob: bytes) -> dict[str, object]:
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError('historical statistics bytes differ from inspected vintage')
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(blob))
    method = re.sub(r'\s+', ' ', reader.pages[183].extract_text() or '')
    for guard in ('total number of instru- ments and extensions',
                  'graph and teletypewriter stations through 1930',
                  'private line telephones through 1934'):
        if guard not in method:
            raise ValueError('telephone definition or historical coverage changed')
    result = parse_table(reader.pages[190].extract_text() or '')
    result['definition'] = ('Instruments and extensions; includes telegraph and '
                            'teletypewriter stations through 1930 and private line '
                            'telephones through 1934')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=Path, default=REPO / 'samples')
    args = parser.parse_args()
    result = extract((args.samples / FILE).read_bytes())
    destination = args.samples / 'remaining-audit-20261028' / 'early_us-telephone-extract.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Extracted R1 and R2 values to {destination}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
