import shutil
from pathlib import Path

import pytest
from world_recent_reproduce import PINS, extract

SAMPLES = Path("samples")


def test_originals_and_population_seams() -> None:
    if not all((SAMPLES / p).is_file() for p in PINS):
        pytest.skip("Original source archive is not present")
    result = extract(SAMPLES)
    assert result["recs1993"]["weighted_total"] == 96631492
    assert result["recs1993"]["percent_by_fuelheat_code"]["1"] == "53.2"
    assert result["acs2024"]["owner_percent"] == "65.3"
    assert result["acs2024"]["other_or_none_percent"] == "12"
    assert result["acs2024"]["one_or_more_vehicle_percent"] == "91.5"


def test_changed_original_bytes_are_rejected(tmp_path: Path) -> None:
    if not all((SAMPLES / p).is_file() for p in PINS):
        pytest.skip("Original source archive is not present")
    for source in PINS:
        destination = tmp_path / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SAMPLES / source, destination)
    changed = tmp_path / "remaining-audit-20261028/world-recent-originals/acs2024-B25045.json"
    changed.write_bytes(changed.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Source changed"):
        extract(tmp_path)
