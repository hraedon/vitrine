"""The HLS review artifact is reproducible and pinned to original bytes."""

import json
from pathlib import Path

import pytest
from world_hls_verify import FILES, verify


def test_hls_original_workbooks_reproduce_artifact() -> None:
    archive = Path(__file__).resolve().parent.parent / 'samples' / '38-jp-housing'
    artifact = archive / 'world-hls-curator-extract.json'
    if not artifact.is_file() or not all((archive / name).is_file() for name in FILES):
        pytest.skip('Original workbooks and curator artifact are not in this archive')
    pytest.importorskip('xlrd')
    assert verify(archive) == json.loads(artifact.read_text(encoding='utf8'))


def test_hls_changed_publisher_bytes_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / next(iter(FILES))
    path.write_bytes(b'not the inspected workbook')
    with pytest.raises(ValueError, match='Publisher source hash differs'):
        verify(tmp_path)
