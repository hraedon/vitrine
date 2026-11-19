"""Reproduce CPI annual-average pairs from pinned registered BLS API responses."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILES = {
    'bls-cpi-annual-1913-1929.json': (
        '68290db70bebfdc3d071602f8d2d4c947aa6377e9ef3a310fedd1e1fbc597715'),
    'bls-cpi-annual-1930-1939.json': (
        'fd3f869ca3b15fc26d236d4830065a4defed004fb6c049abb56af094eb2ba8a7'),
}
ITEMS = {'CUUR0000SAF1': 'Food', 'CUUR0000SEHA': 'Rent of primary residence',
         'CUUR0000SAA': 'Apparel'}
YEARS = {'CUUR0000SAF1': ('1913', '1919', '1920', '1929', '1939'),
         'CUUR0000SEHA': ('1913', '1919', '1920', '1929', '1930', '1939'),
         'CUUR0000SAA': ('1913', '1919')}


def extract(blobs: dict[str, bytes]) -> dict[str, object]:
    values: dict[str, dict[str, str]] = {k: {} for k in ITEMS}
    for file, expected_hash in FILES.items():
        blob = blobs[file]
        if hashlib.sha256(blob).hexdigest() != expected_hash:
            raise ValueError('BLS response bytes changed')
        response = json.loads(blob)
        if response.get('status') != 'REQUEST_SUCCEEDED':
            raise ValueError('BLS request failed')
        series = response['Results']['series']
        if len(series) != len(ITEMS) or {s['seriesID'] for s in series} != set(ITEMS):
            raise ValueError('series missing or duplicated')
        for row in series:
            sid = row['seriesID']
            catalog = row['catalog']
            if (catalog.get('series_id') != sid or catalog.get('item') != ITEMS[sid]
                    or catalog.get('area') != 'U.S. city average'
                    or catalog.get('seasonality') != 'Not Seasonally Adjusted'
                    or catalog.get('survey_abbreviation') != 'CU'):
                raise ValueError('BLS catalog context changed')
            for obs in row['data']:
                year = obs['year']
                if obs['period'] == 'M13' and year in YEARS[sid]:
                    if year in values[sid]:
                        raise ValueError('duplicate annual observation')
                    values[sid][year] = obs['value']
    if any(set(values[sid]) != set(years) for sid, years in YEARS.items()):
        raise ValueError('annual observation missing')
    return {'original_sha256': FILES, 'period': 'M13', 'population': 'CPI-U U.S. city average',
            'seasonality': 'Not Seasonally Adjusted', 'values': values}


def main() -> None:
    path = REPO / 'samples/remaining-audit-20261028'
    result = extract({name: (path / name).read_bytes() for name in FILES})
    (path / 'early_us-cpi-annual-extract.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Extracted annual CPI observations from pinned BLS API responses')


if __name__ == '__main__':
    main()
