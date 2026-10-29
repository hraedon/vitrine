"""Federal Reserve Z.1 source pin and exact balance sheet observations."""
from pathlib import Path

import pytest
from early_us_special_z1_extract import FILE, extract


def test_source_pin() -> None:
    with pytest.raises(ValueError, match='bytes changed'):
        extract(b'other')


def test_original_zip() -> None:
    path = Path(__file__).parent.parent / 'samples' / FILE
    if not path.is_file():
        pytest.skip('Federal Reserve archive missing')
    result = extract(path.read_bytes())
    assert result['observations']['1960']['FL152090005.Q'] == '2092257'
    assert result['observations']['1970']['FL152090005.Q'] == '3876748'
