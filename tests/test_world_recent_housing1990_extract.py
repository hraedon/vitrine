from pathlib import Path

import pytest
from world_recent_housing1990_extract import PINS, extract

ROOT = Path("samples/05-census-housing")


def test_1990_universes() -> None:
    if not all((ROOT / name).is_file() for name in PINS):
        pytest.skip("Census source tables unavailable")
    result = extract(ROOT)
    assert result["plumbing"]["total"] == 102263678
    assert result["telephone"]["total"] == 91947410
    assert result["plumbing"]["population"] != result["telephone"]["population"]


def test_changed_table_rejected(tmp_path: Path) -> None:
    if not all((ROOT / name).is_file() for name in PINS):
        pytest.skip("Census source tables unavailable")
    for name in PINS:
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    path = tmp_path / "plumbing-tab.txt"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        extract(tmp_path)
