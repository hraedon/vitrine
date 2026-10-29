"""Guard source columns and selected historical telephone rows."""
from pathlib import Path

import pytest
from early_us_telephone_extract import FILE, extract, parse_table


def sample_text() -> str:
    return ('Series R 1-12. In thousands, except series R 2 and R 3 '
            'Telephones Total Number Per 1,000 population\n'
            '1900 1,356 17.6\n1915--_ 10,524 103.9\n1925 16,875 144.6\n1935 17,424 136.4\n'
            '1940 21,928 165.1\n1950 43,004 280.9\n1960 74,342 407.8\n'
            '1970 120,218 583.4\n')


def test_source_column_and_year_guards() -> None:
    result = parse_table(sample_text())
    assert result['rows']['1900'] == {'number_thousands': '1,356', 'per_1000_population': '17.6'}
    assert result['rows']['1915']['per_1000_population'] == '103.9'
    assert result['rows']['1970']['number_thousands'] == '120,218'
    with pytest.raises(ValueError, match='header'):
        parse_table(sample_text().replace('Per 1,000 population', 'households'))
    with pytest.raises(ValueError, match='ambiguous'):
        parse_table(sample_text() + '1915 10,524 103.9\n')
    with pytest.raises(ValueError, match='absent'):
        parse_table(sample_text().replace('1950 43,004 280.9', '1950 damaged'))


def test_source_pin_rejects_different_bytes() -> None:
    with pytest.raises(ValueError, match='bytes differ'):
        extract(b'not the source')


def test_archive_reextracts_table() -> None:
    source = Path(__file__).parent.parent / 'samples' / FILE
    if not source.is_file():
        pytest.skip('curator archive not present')
    pytest.importorskip('pypdf')
    result = extract(source.read_bytes())
    assert result['rows']['1900']['per_1000_population'] == '17.6'
    assert result['rows']['1935']['per_1000_population'] == '136.4'
    assert result['rows']['1940']['number_thousands'] == '21,928'
