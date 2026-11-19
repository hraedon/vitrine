from pathlib import Path

import pytest
from world_recent_plumbing_extract import extract

SOURCE = Path("samples/remaining-audit-20261028/us-2000-plumbing-h048.json")


def test_total_and_complete_universe() -> None:
    if not SOURCE.is_file():
        pytest.skip("Census H048 response not in archive")
    result = extract(SOURCE)
    assert result["total"] == 105480101
    assert result["complete"] == 104809115
    assert result["lacking"] == 670986


def test_changed_original_rejected(tmp_path: Path) -> None:
    if not SOURCE.is_file():
        pytest.skip("Census H048 response not in archive")
    path = tmp_path / "changed.json"
    path.write_bytes(SOURCE.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        extract(path)
