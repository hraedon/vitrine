"""Guard selected BLS hourly-earnings data and original bytes."""
from pathlib import Path

import pytest
from early_us_middle_bls_extract import FILE, extract


def test_changed_source_rejected() -> None:
    with pytest.raises(ValueError, match='bytes changed'):
        extract(b'changed')


def test_original_bulletin_rows() -> None:
    path = Path(__file__).parent.parent / 'samples' / FILE
    if not path.is_file():
        pytest.skip('original source archive missing')
    pytest.importorskip('pypdf')
    result = extract(path.read_bytes())
    assert (result['1947'], result['1960'], result['1970']) == ('1.131', '2.09', '3.23')
