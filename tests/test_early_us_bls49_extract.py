"""Original Bulletin No. 49 extraction and source-byte rejection."""
from pathlib import Path

import pytest
from early_us_bls49_extract import FILE, extract, unique


def test_unique_rejects_ambiguous_or_missing() -> None:
    with pytest.raises(ValueError, match='ambiguous'):
        unique(r'cost (\d+)', 'cost 1 cost 2')
    with pytest.raises(ValueError, match='absent'):
        unique(r'cost (\d+)', 'nothing')


def test_changed_source_bytes_rejected() -> None:
    with pytest.raises(ValueError, match='original bytes'):
        extract(b'not source')


def test_original_archive_extracts_source_narrative() -> None:
    path = Path(__file__).parent.parent / 'samples' / FILE
    if not path.is_file():
        pytest.skip('original Bulletin No. 49 not present')
    pytest.importorskip('pypdf')
    result = extract(path.read_bytes())
    assert result['income'] == '827.19'
    assert result['food_share'] == '42.54'
    assert result['rent_share'] == '12.95'
    assert result['family_size'] == '5.31'
