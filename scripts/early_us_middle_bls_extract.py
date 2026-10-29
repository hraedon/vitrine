"""Extract selected 1947â€“1970 BLS private-sector hourly earnings."""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILE = '28-bls-employment-benchmarks/emp-benchmark-1909-1984-vol2.pdf'
SHA256 = '576c7b81afc613cc4313644e367739c14c06f83dd003ea88c032ea1d835b305b'


def parse_page(text: str) -> dict[str, str]:
    start = text.find('TOTAL PRIVATE')
    heading = ' '.join(text[:start].split())
    required = 'PRODUCTION OR NONSUPERVISORY WORKERS ON PRIVATE NONAGRICULTURAL'
    if start < 0 or required not in heading:
        raise ValueError('population or table heading changed')
    lines = [s.strip() for s in text[start:].splitlines() if s.strip()]
    try:
        marker = lines.index('AVERAGE HOURLY EARNINGS')
        if lines[marker + 1] != 'IN CURRENT DOUARS':
            raise ValueError('current-dollar column heading changed')
        years = [x for x in lines[1:marker] if re.fullmatch(r'19\d\d', x)]
        values = lines[marker + 2:marker + 2 + len(years)]
        if years != [str(x) for x in range(1947, 1964)]:
            raise ValueError('annual year column changed')
        if any(re.fullmatch(r'\d+\.\d+', x) is None for x in values):
            raise ValueError('annual values are damaged')
        rows = dict(zip(years, values, strict=True))
        lines1970 = [s for s in lines if re.match(r'^1970\s+\d+\.\d+', s)]
        if len(lines1970) != 1:
            raise ValueError('1970 row missing or ambiguous')
        rows['1970'] = lines1970[0].split()[1]
    except (IndexError, ValueError) as e:
        raise ValueError('selected annual table cannot be parsed') from e
    return {'source_sha256': SHA256, 'pdf_page': '287', 'printed_page': '909',
            'unit': 'current dollars per hour',
            'population': ('Production or nonsupervisory workers on private nonagricultural '
                           'payrolls'),
            '1947': rows['1947'], '1960': rows['1960'], '1970': rows['1970']}


def extract(blob: bytes) -> dict[str, str]:
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError('original BLS bulletin bytes changed')
    from pypdf import PdfReader

    return parse_page(PdfReader(io.BytesIO(blob)).pages[286].extract_text() or '')


def main() -> None:
    path = REPO / 'samples/remaining-audit-20261028/middle_bls_hourly_extract.json'
    path.write_text(json.dumps(extract((REPO / 'samples' / FILE).read_bytes()), indent=2)
                    + '\n', encoding='utf-8', newline='\n')
    print('Extracted selected BLS annual hourly observations')


if __name__ == '__main__':
    main()
