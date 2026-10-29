"""Reproduce selected Census historic plumbing and heating fuel figures.

Reads original Census text bytes pinned below. The JSON output is a curator
extraction, not independent publisher data. Plumbing totals and complete shares
are calculated from source counts using decimal half-up rounding once; the 1940
plumbing categories require the separate private-bath/toilet definition seam.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

PINS = {
    'plumbing-tab.txt': '56dcbdabfcdb340ccf23b988779725a3165b0e150d62795848a9ddd4b767132b',
    'fuels1940.txt': 'fad774386aeb6debd0fb3abf5844efa28897ccafe695c3a164ef405f4ec05b79',
    'fuels1950.txt': '6d506e2e566fff5d38a9b68c3a8de2c55e8097e3d98ff672793cc1697c4a423e',
    'fuels1960.txt': 'a155cf62623a84e9cf508580cd000b77e17779ce21505e5b9ea68e30a006e68e',
    'fuels1970.txt': '8d4d3d62e5eec6d74b3da7ec3d8e9fa7bc1af6a43260653e06d9900c539087be',
    'fuels1980.txt': 'e0a241cf8dea73e7902803eed60a11267ee3836e7ac9b8a64968175cc0bb9e1c',
    'phone-tab.txt': 'f0029b5ad7a1974e90d69e24f19584548a23c6343efdd033dee3f872f31e1a27',
}
YEARS = (1940, 1950, 1960, 1970, 1980)
PLUMBING_GUARDS = {
    1940: (19174344, 15852098, '45.3%'),
    1950: (28729475, 15772717, '35.5%'),
    1960: (48537001, 9777783, '16.8%'),
    1970: (62984221, 4672345, '6.9%'),
    1980: (84359133, 2333690, '2.7%'),
}


def extract(root: Path) -> dict[str, object]:
    texts = {}
    for name, digest in PINS.items():
        blob = (root / name).read_bytes()
        if hashlib.sha256(blob).hexdigest() != digest:
            raise ValueError(f'Publisher bytes changed: {name}')
        texts[name] = blob.decode('utf-8-sig')
    plumbing = texts['plumbing-tab.txt']
    blocks = re.findall(r'(?m)^US\s+([\d,]+)\s+([\d,]+)\s+([\d.]+%)\s+'
                        r'([\d,]+)\s+([\d,]+)\s+([\d.]+%)\s*$', plumbing)
    if len(blocks) != 3 or 'Complete  Lacking complete' not in plumbing:
        raise ValueError('Plumbing source layout changed')
    by_year: dict[int, tuple[str, ...]] = {}
    for (newer, older), row in zip(((1990, 1980), (1970, 1960), (1950, 1940)), blocks, strict=True):
        by_year[newer], by_year[older] = row[:3], row[3:]
    phone = texts['phone-tab.txt']
    phone_blocks = re.findall(r'(?m)^\s*US\s+([\d,]+)\s+([\d,]+)\s+([\d.]+%)\s+'
                              r'([\d,]+)\s+([\d,]+)\s+([\d.]+%)\s*$', phone)
    if len(phone_blocks) != 2 or 'No telephone in unit' not in phone:
        raise ValueError('Telephone source layout changed')
    phone_years = {1980: phone_blocks[0][3:], 1970: phone_blocks[1][:3]}
    phone_guards = {1970: (55176700, 8273047, '13.0%'), 1980: (74719996, 5669677, '7.1%')}
    population_basis = {1940: 'all dwelling units reporting', 1950: 'all dwelling units reporting',
                        1960: 'all housing units', 1970: 'all year-round housing units',
                        1980: 'housing units including vacant units'}
    data: dict[str, object] = {}
    for year in YEARS:
        complete, lacking, percent = by_year[year]
        c, lack = int(complete.replace(',', '')), int(lacking.replace(',', ''))
        if (c, lack, percent) != PLUMBING_GUARDS[year]:
            raise ValueError(f'Unexpected plumbing row {year}')
        total = c + lack
        share = (Decimal(c) * 100 / Decimal(total)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        fueltext = texts[f'fuels{year}.txt']
        if not fueltext.startswith(str(year)) or 'Occupied' not in fueltext[:300]:
            raise ValueError(f'Fuel header changed {year}')
        rows = re.findall(r'(?m)^US\s+(.+?)\s*$', fueltext)
        if len(rows) != 1:
            raise ValueError(f'Expected one national fuel row for {year}')
        fields = rows[0].split()
        if len(fields) < 9:
            raise ValueError(f'Fuel row incomplete for {year}')
        names = ('gas', 'bottled_lp', 'electricity', 'fuel_oil_kerosene', 'coal_coke',
                 'wood', 'other', 'no_fuel')
        values = dict(zip(names, fields[1:9], strict=True))
        if year == 1940 and 'Utility gas and Bottled gas were combined in 1940.' not in fueltext:
            raise ValueError('1940 combined-gas note missing')
        data[str(year)] = {
            'plumbing': {'complete_count': c, 'lacking_count': lack, 'total_reporting': total,
                         'complete_pct_rounded_once': str(share), 'lacking_pct_printed': percent,
                         'source': 'plumbing-tab.txt', 'population_basis': population_basis[year]},
            'heating': {'occupied_reporting_count': int(fields[0]), 'percentages_printed': values,
                        'source': f'fuels{year}.txt', 'gas_combined': year == 1940},
        }
        if year in phone_years:
            yes, no, no_pct = phone_years[year]
            yes_count, no_count = int(yes.replace(',', '')), int(no.replace(',', ''))
            if (yes_count, no_count, no_pct) != phone_guards[year]:
                raise ValueError(f'Unexpected telephone row {year}')
            total_phone = yes_count + no_count
            phone_share = (Decimal(yes_count) * 100 / Decimal(total_phone)).quantize(
                Decimal('0.1'), rounding=ROUND_HALF_UP)
            data[str(year)]['telephone'] = {
                'with_phone_count': yes_count, 'without_phone_count': no_count,
                'total_reporting': total_phone, 'with_phone_pct_rounded_once': str(phone_share),
                'without_phone_pct_printed': no_pct, 'source': 'phone-tab.txt',
                'population_basis': 'occupied housing units reporting telephone status',
            }
    return {'kind': 'curator extraction; not independent publisher bytes',
            'publisher_sha256': PINS, 'years': data}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('housing_archive', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = extract(args.housing_archive)
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n',
                               encoding='utf-8', newline='\n')
    print('Verified Census housing rows for ' + ', '.join(map(str, YEARS)))
