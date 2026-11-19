"""SEER original table and source pin checks."""
from pathlib import Path

import pytest
from early_us_special_seer_extract import FILE, extract


def test_source_pin() -> None:
    with pytest.raises(ValueError, match='bytes changed'):
        extract(b'other')


def test_original_seer_table() -> None:
    path = Path(__file__).parent.parent / 'samples' / FILE
    if not path.is_file():
        pytest.skip('original SEER report missing')
    pytest.importorskip('pypdf')
    result = extract(path.read_bytes())
    assert result['1975-1979'] == '48.9'
    assert result['1980-1984'] == '50.2'
