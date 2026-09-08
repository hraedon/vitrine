"""CES refreshes retain publisher bytes and require distinct calendar months."""

import hashlib
import importlib.util
import json
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def extractor(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "ces_extractor", Path(__file__).parents[1] / "scripts/bls_ces_extract.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "START_YEAR", 1950)
    monkeypatch.setattr(module, "END_YEAR", 1950)
    monkeypatch.setattr(module, "ARCHIVE_DIR", tmp_path)
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    return module


def response(duplicate: bool = False) -> bytes:
    rows = [{"year": "1950", "period": f"M{i:02}", "value": "1.315"} for i in range(1, 13)]
    if duplicate:
        rows[-1]["period"] = "M11"
    return json.dumps({"status": "REQUEST_SUCCEEDED", "Results": {
        "series": [{"seriesID": "CES3000000008", "data": rows}],
    }}, indent=2).encode()


class Response:
    status_code = 200

    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self) -> None:
        pass

    def json(self) -> object:
        return json.loads(self.content)


def test_refresh_saves_exact_response_without_request_key(
    extractor: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    blob = response()
    monkeypatch.setattr(extractor.requests, "post", lambda *a, **kw: Response(blob))
    months = extractor._pull_months("CES3000000008", "synthetic-request-secret")
    saved = list(tmp_path.glob("*.json"))
    assert len(saved) == 1 and saved[0].read_bytes() == blob
    assert hashlib.sha256(blob).hexdigest() in saved[0].name
    assert b"synthetic-request-secret" not in saved[0].read_bytes()
    assert extractor._annualize(months) == {1950: Decimal("1.3150")}


def test_duplicate_month_is_not_an_annual_average(
    extractor: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    monkeypatch.setattr(extractor.requests, "post", lambda *a, **kw: Response(response(True)))
    with pytest.raises(RuntimeError, match="duplicate month"):
        extractor._pull_months("CES3000000008", None)
    assert not list(tmp_path.iterdir())


def test_incomplete_calendar_year_is_not_emitted(extractor: ModuleType) -> None:
    months = {f"M{i:02}": Decimal("1.3") for i in range(1, 12)}
    assert extractor._annualize({1950: months}) == {}
