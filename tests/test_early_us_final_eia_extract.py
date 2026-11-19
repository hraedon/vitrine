from pathlib import Path

import pytest
from early_us_final_eia_extract import extract


def test_pinned_air_conditioning_rows() -> None:
    source = Path("samples/remaining-audit-20261028/final-eia-stb0206.xls")
    if not source.is_file():
        pytest.skip("inspected EIA source archive required")
    result = extract(source.read_bytes())
    assert result["central"] == {"1978": 23, "1980": 27, "1993": 44}
    assert result["window_wall"] == {"1978": 33, "1980": 30, "1993": 25}
    assert result["none"] == {"1978": 44, "1980": 43, "1993": 32}


def test_rejects_changed_source() -> None:
    with pytest.raises(ValueError, match="hash"):
        extract(b"untrusted")
