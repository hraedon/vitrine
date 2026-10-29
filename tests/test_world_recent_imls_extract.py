from pathlib import Path

import pytest
from world_recent_imls_extract import extract

SOURCE = Path("samples/remaining-audit-20261028/recent_us-originals/pls_fy2020_csv.zip")


def test_total_and_imputation_flags() -> None:
    if not SOURCE.is_file():
        pytest.skip("IMLS source ZIP unavailable")
    result = extract(SOURCE)
    assert result["reference_transactions"] == 139263801
    assert result["flags"] == {"IA20": 1, "IF20": 42, "R_20": 8}


def test_changed_archive_rejected(tmp_path: Path) -> None:
    if not SOURCE.is_file():
        pytest.skip("IMLS source ZIP unavailable")
    path = tmp_path / "changed.zip"
    path.write_bytes(SOURCE.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed"):
        extract(path)
