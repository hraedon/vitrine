"""Extract selected 1901 household means from Bulletin No. 49.

The original report's printed narrative supplies the values and survey limits;
this curator-only tool requires pypdf and pins the publisher's original bytes.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILE = '03-bls-historical/bls_v08_0049_1903.pdf'
SHA256 = '34a9af272e6461a5074eb97797b3c77bb6ba249445adbc8a8ad4058581a42638'


def unique(pattern: str, text: str) -> str:
    matches = re.findall(pattern, text)
    if len(matches) != 1:
        raise ValueError('required observation absent or ambiguous')
    return str(matches[0]).replace(',', '')


def parse_pages(first: str, second: str, third: str) -> dict[str, str]:
    a, b, c = (' '.join(x.split()) for x in (first, second, third))
    for guard in ('1901', '2,567 families', 'wage worker or a salaried man',
                  'income for the year', 'expenditure for all purposes'):
        if guard not in a:
            raise ValueError('1901 population or source definition changed')
    patterns = {
        'family_size': r'consisted on an average of (\d+\.\d+) persons',
        'income_ceiling': r'earning not over \$([\d,]+) during the year',
        'income': r'families from all sources was \$(\d+\.\d+)',
        'expenditure': r'for all purposes was \$(\d+\.\d+)',
        'food': r'expenditure for food was \$(\d+\.\d+)',
        'food_share': r'per family, or (\d+\.\d+) per cent of the average expenditure',
        'rent_share': r'no prices for the several years are available, made up (\d+\.\d+) per cent',
        'clothing_share': r'consist of clothing (\d+\.\d+) per cent',
        'fuel_share': r'fuel and lighting (\d+\.\d+) per cent',
        'furniture_share': r'furniture and utensils (\d+\.\d+) per cent',
        'tobacco_share': r'tobacco (\d+\.\d+) per cent',
    }
    result = {key: unique(pattern, a if key in ('family_size','income_ceiling','income',
              'expenditure','food','food_share') else (c if key in ('furniture_share',
              'tobacco_share') else b)) for key, pattern in patterns.items()}
    if 'mortgage, taxes, property and life insurance' not in b:
        raise ValueError('combined category description is missing')
    result.update(source_sha256=SHA256, year='1901', pdf_pages='6,8,9',
                  population=('2567 families in 33 states; head a wage worker or salaried man '
                              'earning at most $1200'))
    return result


def extract(blob: bytes) -> dict[str, str]:
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError('Bulletin No. 49 original bytes changed')
    from pypdf import PdfReader

    pages = PdfReader(io.BytesIO(blob)).pages
    preface = ' '.join((pages[4].extract_text() or '').split())
    if '2,567 families in 33 States' not in preface or '1901' not in preface:
        raise ValueError('sample geography or year changed')
    return parse_pages(*(pages[i].extract_text() or '' for i in (5, 7, 8)))


def main() -> None:
    result = extract((REPO / 'samples' / FILE).read_bytes())
    target = REPO / 'samples/remaining-audit-20261028/early_us-bls49-extract.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Extracted original Bulletin No. 49 narrative to {target}')


if __name__ == '__main__':
    main()
