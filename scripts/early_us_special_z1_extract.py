"""Extract the Federal Reserve's pinned Z.1 household balance sheet observations."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

REPO = Path(__file__).resolve().parent.parent
FILE = 'remaining-audit-20261028/special-z1-visualization.zip'
SHA256 = '379ced866e8da615a23b10d84cfd15c5271c49f1776fc0292d477f3b198ace93'
COLUMNS = {
    'FL152090005.Q': 'Households and nonprofit organizations; Net Worth',
    'FL152000005.Q': 'Households and nonprofit organizations; Total Assets',
    'FL154190005.Q': 'Households and nonprofit organizations; Total Liabilities',
}


def extract(blob: bytes) -> dict[str, object]:
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError('Federal Reserve ZIP bytes changed')
    with ZipFile(io.BytesIO(blob)) as z:
        dictionary = list(csv.DictReader(io.StringIO(
            z.read('z1-visualization-dictionary.txt').decode('utf-8-sig')), delimiter='\t'))
        for key, description in COLUMNS.items():
            matches = [r for r in dictionary if r['series'] == key]
            if (len(matches) != 1 or matches[0]['description'] != description
                    or matches[0]['units'] != 'Millions of dollars'):
                raise ValueError('Fed series definition changed')
        rows = list(csv.DictReader(io.StringIO(
            z.read('z1-visualization-data.csv').decode('utf-8-sig'))))
    observations: dict[str, dict[str, str]] = {}
    for year in ('1960', '1970'):
        matches = [r for r in rows if r['date'] == year + ':Q4']
        if len(matches) != 1:
            raise ValueError('quarter absent or ambiguous')
        row = matches[0]
        selected = {key: row[key].strip() for key in COLUMNS}
        if any(not x.isdigit() for x in selected.values()):
            raise ValueError('nonliteral source values')
        if int(selected['FL152000005.Q']) - int(selected['FL154190005.Q']) != int(
            selected['FL152090005.Q']
        ):
            raise ValueError('source balance sheet identity changed')
        observations[year] = selected
    return {'source_sha256': SHA256, 'unit': 'millions of dollars',
            'population': 'Households and nonprofit organizations', 'period': 'Q4',
            'observations': observations}


def main() -> None:
    path = REPO / 'samples/remaining-audit-20261028/special-z1-extract.json'
    path.write_text(json.dumps(extract((REPO / 'samples' / FILE).read_bytes()), indent=2)
                    + '\n', encoding='utf-8', newline='\n')
    print('Extracted two Federal Reserve household balance sheets')


if __name__ == '__main__':
    main()
