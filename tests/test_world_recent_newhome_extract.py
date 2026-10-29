from pathlib import Path

import pytest
from world_recent_newhome_extract import extract

SOURCE = Path("samples/remaining-audit-20261028/recent_us-originals/squarefeet_cust.xls")


def test_new_construction_years_and_population() -> None:
    if not SOURCE.is_file():
        pytest.skip("Census XLS unavailable")
    pytest.importorskip("xlrd")
    data = extract(SOURCE)
    assert data["years"]["1990"]["median_sqft"] == 1905
    assert data["years"]["2024"]["median_sqft"] == 2146
    assert data["years"]["2024"]["population"] == "new single-family houses completed"


def test_changed_workbook_rejected(tmp_path: Path) -> None:
    if not SOURCE.is_file():
        pytest.skip("Census XLS unavailable")
    path = tmp_path / "changed.xls"
    path.write_bytes(SOURCE.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        extract(path)
