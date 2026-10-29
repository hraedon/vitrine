"""Historical census extraction rejects altered bytes and replays the archive."""

import json
import shutil
from pathlib import Path

import pytest
from world_middle_housing_extract import PINS, extract


def test_housing_archive_reproduces_artifact() -> None:
    samples = Path(__file__).resolve().parent.parent / 'samples'
    archive = samples / '05-census-housing'
    artifact = samples / 'remaining-audit-20261028' / 'world-middle-housing-extract.json'
    if not artifact.exists() or not all((archive / name).is_file() for name in PINS):
        pytest.skip('Original Census files and curator artifact are not in this archive')
    result = extract(archive)
    assert result == json.loads(artifact.read_text(encoding='utf-8'))
    assert result['years']['1950']['plumbing']['complete_pct_rounded_once'] == '64.6'
    assert result['years']['1970']['plumbing']['complete_pct_rounded_once'] == '93.1'
    assert result['years']['1940']['plumbing']['population_basis'] == 'all dwelling units reporting'
    assert result['years']['1970']['plumbing']['population_basis'] == 'all year-round housing units'
    assert result['years']['1970']['telephone']['population_basis'] == (
        'occupied housing units reporting telephone status'
    )
    assert result['years']['1970']['telephone']['with_phone_pct_rounded_once'] == '87.0'
    assert result['years']['1980']['telephone']['with_phone_pct_rounded_once'] == '92.9'
    expected = {
        '1940': ['11.3%', 'NA', 'NA', '10.0%', '54.7%', '22.8%', '0.4%', '0.8%'],
        '1950': ['26.6%', '2.3%', '0.7%', '22.6%', '34.6%', '10.0%', '1.8%', '1.4%'],
        '1960': ['43.1%', '5.1%', '1.8%', '32.4%', '12.2%', '4.2%', '0.4%', '0.9%'],
        '1970': ['55.2%', '6.0%', '7.7%', '26.0%', '2.9%', '1.3%', '0.4%', '0.6%'],
        '1980': ['53.1%', '5.6%', '18.4%', '18.2%', '0.6%', '3.2%', '0.2%', '0.7%'],
    }
    for year, values in expected.items():
        assert list(result['years'][year]['heating']['percentages_printed'].values()) == values
    assert result['years']['1940']['heating']['gas_combined'] is True
    assert result['years']['1950']['heating']['gas_combined'] is False


def test_housing_extraction_refuses_changed_source(tmp_path: Path) -> None:
    (tmp_path / next(iter(PINS))).write_bytes(b'not the inspected source')
    with pytest.raises(ValueError, match='Publisher bytes changed'):
        extract(tmp_path)


def test_real_archive_mutation_cannot_reuse_the_source_pin(tmp_path: Path) -> None:
    archive = Path(__file__).resolve().parent.parent / 'samples' / '05-census-housing'
    if not all((archive / name).is_file() for name in PINS):
        pytest.skip('Original Census files are not in this archive')
    for name in PINS:
        shutil.copyfile(archive / name, tmp_path / name)
    target = tmp_path / 'fuels1970.txt'
    blob = target.read_bytes()
    assert b'55.2%' in blob
    target.write_bytes(blob.replace(b'55.2%', b'55.3%', 1))
    with pytest.raises(ValueError, match='Publisher bytes changed'):
        extract(tmp_path)
