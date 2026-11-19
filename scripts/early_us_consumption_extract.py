"""Extract CDC, NIAAA and FHWA historical consumption and fatality observations."""
from __future__ import annotations

import hashlib
import html
import io
import json
import re
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILES = {
    'cdc': ('34-smoking/mmwr-tobacco-surveillance-1900-1994.html',
            '02e4e219a65571dd287ca9e6d13dae1d3138c290f410550ea63eea33c85bb277'),
    'niaaa': ('34-smoking/niaaa-surveillance-122.pdf',
              '71f1e8531f2de32138f99d20b239ec78215a23b50070294fbb80671507bc222a'),
    'fhwa': ('44-road-workplace-deaths/fhwa-fi200-highway-statistics-2023.html',
             'e5cb5e304b9c86f3124543e27dd4e9e0e18f2d1d8a40bc9891805332f88490d6'),
}


def parse_cdc(text: str) -> dict[str, object]:
    text = html.unescape(text)
    if 'U.S. military forces overseas are included' not in text:
        raise ValueError('military inclusion footnote missing')
    start = text.index('TABLE 1. Total and per capita yearly consumption')
    stop = text.index('Table_2', start)
    table1 = text[start:stop]
    per_capita: dict[str, str] = {}
    for year in (1900, 1910, 1920, 1930, 1940, 1950, 1963, 1970, 1980):
        rows = re.findall(rf'(?m)^\s*{year}\s+([\d.]+)\s+([\d,]+)\s', table1)
        if len(rows) != 1:
            raise ValueError('CDC cigarette row absent or ambiguous')
        per_capita[str(year)] = rows[0][1].replace(',', '')
    start = text.index('TABLE  2. Percentage of adults', stop)
    end = text.index('Source:  National Health Interview Surveys:', start)
    table2 = text[start:end]
    for guard in ('Persons >=18 years of age', 'Current smokers reported smoking >=100 cigarettes',
                  '1965    1966   1970   1974   1978   1979   1980'):
        if guard not in table2:
            raise ValueError('NHIS population, definition, or column headings changed')
    current: list[str] = []
    for label in ('Total population', 'Male', 'Female'):
        pattern = (rf'(?m)^\s*{label}\s*\n\s*Current\s+'
                   r'((?:\d+\.\d+\s+){13})')
        matches = re.findall(pattern, table2)
        if len(matches) != 1:
            raise ValueError('NHIS labeled current-smoker row absent or ambiguous')
        current.append(matches[0])
    smoking: dict[str, dict[str, str]] = {}
    for year, col in (('1965', 0), ('1970', 2), ('1980', 6)):
        smoking[year] = dict(zip(('total', 'male', 'female'),
                                (row.split()[col] for row in current), strict=True))
    return {'source_sha256': FILES['cdc'][1], 'cigarettes_per_adult': per_capita,
            'smoking_prevalence': smoking, 'adult_age': '18 and older',
            'military': 'Overseas military included in per-capita consumption 1930-1994'}


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th') and self.row is not None:
            self.cell = ''

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag: str) -> None:
        if tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.row.append(' '.join(self.cell.split()))
            self.cell = None
        if tag == 'tr' and self.row:
            self.rows.append(self.row)
            self.row = None


def parse_fhwa(text: str) -> dict[str, object]:
    for guard in ('Table FI-200', 'PER 100 MILLION', 'HIGHWAY <br />', 'FATALITIES'):
        if guard not in text:
            raise ValueError('FHWA table or column header changed')
    parser = TableParser()
    parser.feed(text)
    result: dict[str, dict[str, str]] = {}
    for year in (1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1972, 1980, 1989, 1990):
        rows = [r for r in parser.rows if r[0] == str(year)]
        if len(rows) != 1 or len(rows[0]) != 10:
            raise ValueError('FHWA row absent or ambiguous')
        row = rows[0]
        if re.fullmatch(r'\d+\.\d{2}', row[7]) is None:
            raise ValueError('FHWA rate column damaged')
        result[str(year)] = {'fatalities': row[5].replace(',', ''), 'per_100m_vmt': row[7]}
    return {'source_sha256': FILES['fhwa'][1], 'table': 'FI-200', 'rows': result}


def parse_niaaa(page13: str, page14: str) -> dict[str, object]:
    texts = [page13, page14]
    for text in texts:
        normalized = ' '.join(text.split())
        for guard in ('Table 1. Apparent per capita ethanol consumption',
                      'population ages 15 and older prior to 1970',
                      'population ages 14 and older thereafter',
                      'Year Beer Wine Spirits All beverages'):
            if guard not in normalized:
                raise ValueError('NIAAA table heading or age denominator changed')
    combined = '\n'.join(texts)
    result: dict[str, str] = {}
    for year in (1934, 1940, 1950, 1960, 1970, 1980, 1981):
        rows = re.findall(rf'(?m)^\s*{year}\s+\.+\s+(\d+\.\d+)\s+'
                          r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$', combined)
        if len(rows) != 1:
            raise ValueError('NIAAA row absent or ambiguous')
        result[str(year)] = rows[0][3]
    return {'source_sha256': FILES['niaaa'][1], 'all_beverages': result,
            'unit': 'gallons ethanol per person per year',
            'age_basis': '15 and older before 1970; 14 and older from 1970'}


def extract(blobs: dict[str, bytes]) -> dict[str, object]:
    for key, (_, expected) in FILES.items():
        if hashlib.sha256(blobs[key]).hexdigest() != expected:
            raise ValueError('original source bytes changed: ' + key)
    from pypdf import PdfReader
    pages = PdfReader(io.BytesIO(blobs['niaaa'])).pages
    return {'cdc': parse_cdc(blobs['cdc'].decode('latin-1')),
            'fhwa': parse_fhwa(blobs['fhwa'].decode('utf-8')),
            'niaaa': parse_niaaa(pages[12].extract_text() or '', pages[13].extract_text() or '')}


def main() -> None:
    blobs = {key: (REPO / 'samples' / path).read_bytes() for key, (path, _) in FILES.items()}
    target = REPO / 'samples/remaining-audit-20261028/early_us-consumption-extract.json'
    target.write_text(json.dumps(extract(blobs), indent=2, ensure_ascii=False) + '\n',
                      encoding='utf-8', newline='\n')
    print('Extracted guarded CDC, NIAAA and FHWA observations')


if __name__ == '__main__':
    main()
