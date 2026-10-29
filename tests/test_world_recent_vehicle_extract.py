from pathlib import Path

import pytest
from world_recent_vehicle_extract import extract

SOURCE = Path("samples/05-census-housing/bts-vehicle-availability.xlsx")


def test_vehicle_complements_and_years() -> None:
    if not SOURCE.is_file():
        pytest.skip("BTS workbook not in local archive")
    result = extract(SOURCE)
    assert result["years"]["1960"]["no_vehicle_percent"] == "21.5"
    assert result["years"]["1960"]["one_or_more_percent"] == "78.5"
    assert result["years"]["1970"]["no_vehicle_percent"] == "17.5"
    assert result["years"]["1970"]["one_or_more_percent"] == "82.5"
    assert result["years"]["1980"]["no_vehicle_percent"] == "12.9"
    assert result["years"]["1980"]["one_or_more_percent"] == "87.1"
    assert result["years"]["1990"]["one_or_more_percent"] == "88.5"
    assert result["years"]["2000"]["one_or_more_percent"] == "89.7"
    assert result["years"]["2010"]["one_or_more_percent"] == "90.9"


def test_changed_workbook_is_rejected(tmp_path: Path) -> None:
    if not SOURCE.is_file():
        pytest.skip("BTS workbook not in local archive")
    path = tmp_path / "changed.xlsx"
    path.write_bytes(SOURCE.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        extract(path)
