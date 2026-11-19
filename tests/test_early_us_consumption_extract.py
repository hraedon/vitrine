"""Ensure the original three sources reproduce selected independent series."""
from pathlib import Path

import pytest
from early_us_consumption_extract import FILES, extract, parse_cdc


def test_source_replacement_rejected() -> None:
    with pytest.raises(ValueError, match='bytes changed'):
        extract({key: b'changed' for key in FILES})


def test_archive_replays_three_sources() -> None:
    root = Path(__file__).parent.parent / 'samples'
    if not all((root / path).exists() for path, _ in FILES.values()):
        pytest.skip('curator originals unavailable')
    pytest.importorskip('pypdf')
    result = extract({key: (root / path).read_bytes() for key, (path, _) in FILES.items()})
    assert result['cdc']['smoking_prevalence']['1965']['total'] == '42.4'
    assert result['cdc']['cigarettes_per_adult']['1963'] == '4345'
    assert result['niaaa']['all_beverages']['1970'] == '2.52'
    assert result['fhwa']['rows']['1989']['per_100m_vmt'] == '2.17'


def test_current_smoking_row_labels_are_required() -> None:
    source = Path(__file__).parent.parent / 'samples' / FILES['cdc'][0]
    if not source.is_file():
        pytest.skip('CDC original unavailable')
    text = source.read_bytes().decode('latin-1').replace('\r\n', '\n')
    damaged = text.replace(' Total population\n  Current', ' Total population\n  Missing', 1)
    with pytest.raises(ValueError, match='labeled'):
        parse_cdc(damaged)
