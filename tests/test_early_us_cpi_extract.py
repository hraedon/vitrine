"""CPI annual qualifier pins originals and rejects unapproved bytes."""
from pathlib import Path

import pytest
from early_us_cpi_extract import FILES, extract


def test_source_bytes_are_pinned() -> None:
    with pytest.raises(ValueError, match='bytes changed'):
        extract({name: b'modified' for name in FILES})


def test_original_annual_cpi_responses() -> None:
    root = Path(__file__).parent.parent / 'samples/remaining-audit-20261028'
    if not all((root / name).is_file() for name in FILES):
        pytest.skip('registered API response archive not present')
    result = extract({name: (root / name).read_bytes() for name in FILES})
    assert result['values']['CUUR0000SEHA']['1913'] == '21.0'
    assert result['values']['CUUR0000SAF1']['1939'] == '11.8'
