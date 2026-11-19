from pathlib import Path

import pytest
from world_recent_cable_extract import extract

SOURCE = Path("samples/09-fcc/FCC-07-206A1.pdf")


def test_cable_and_tv_counts() -> None:
    if not SOURCE.is_file():
        pytest.skip("FCC source report unavailable")
    pytest.importorskip("pypdf")
    data = extract(SOURCE)
    assert data["basic_cable_millions"] == "65.3"
    assert data["tv_households_millions"] == "110.2"


def test_changed_report_rejected(tmp_path: Path) -> None:
    if not SOURCE.is_file():
        pytest.skip("FCC source report unavailable")
    path = tmp_path / "changed.pdf"
    path.write_bytes(SOURCE.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        extract(path)
