"""Extract 1975â€“84 five-year relative survival from SEER CSR Table 2.9."""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILE = 'remaining-audit-20261028/special-seer.pdf'
SHA256 = '8049fb982770d59f9c6e7cadf0f0fa3fcd10da458dc2e88cf10c9ffa36feb21c'


def parse_page(text: str) -> dict[str, str]:
    for guard in ('Table 2.9', 'All Cancer Sites (Invasive)', 'All Races, Males and Females',
                  'Relative Survival', 'Based on the SEER 9 areas'):
        if guard not in text:
            raise ValueError('SEER table context changed')
    if not re.search(r'1975-\s+1980-\s+1985-\s+1990-\s*\n\s*1979\s+1984', text):
        raise ValueError('diagnosis period headings changed')
    rows = re.findall(r'(?m)^\s*5-year\s+(\d+\.\d+)\s+(\d+\.\d+)\s+', text)
    if len(rows) != 1:
        raise ValueError('five-year row absent or ambiguous')
    return {'source_sha256': SHA256, 'table': '2.9', 'pdf_page': '1',
            'population': 'SEER 9 areas; all races; males and females; invasive cancer',
            'measure': 'five-year relative survival percent',
            '1975-1979': rows[0][0], '1980-1984': rows[0][1]}


def extract(blob: bytes) -> dict[str, str]:
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError('original SEER bytes changed')
    from pypdf import PdfReader
    return parse_page(PdfReader(io.BytesIO(blob)).pages[0].extract_text() or '')


def main() -> None:
    result = extract((REPO / 'samples' / FILE).read_bytes())
    path = REPO / 'samples/remaining-audit-20261028/special-seer-extract.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Extracted SEER relative survival periods from original table')


if __name__ == '__main__':
    main()
