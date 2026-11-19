"""The FRED rate extractor must preserve precision and identify real calendar years."""

import datetime
from pathlib import Path

import ahetpi_extract as extractor
import openpyxl
import pytest

from vitrine.model import Basis, SeriesKind
from vitrine.series import load_series


def workbook(path: Path, months: list[int]) -> None:
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Monthly"
    sheet.append(["date", "earnings"])
    for month in months:
        sheet.append([datetime.datetime(1950, month, 1), 1.3158])
    book.save(path)
    book.close()


def configure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, months: list[int]) -> Path:
    path = tmp_path / "monthly.xlsx"
    workbook(path, months)
    directory = tmp_path / "series"
    directory.mkdir()
    monkeypatch.setattr(extractor, "XLSX", path)
    monkeypatch.setattr(extractor, "OUT", directory / "rates.toml")
    monkeypatch.setattr(extractor, "REPO", tmp_path)
    monkeypatch.setattr(extractor, "START_YEAR", 1950)
    monkeypatch.setattr(extractor, "END_YEAR", 1950)
    return tmp_path


def test_fred_emission_keeps_subcent_monetary_rate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    configure(monkeypatch, tmp_path, list(range(1, 13)))
    assert extractor.main() == 0
    candidate = load_series(tmp_path)["hourly-earnings-total-private"]
    assert candidate.values == {1950: 1.3158}
    assert candidate.kind is SeriesKind.MONETARY_RATE
    assert candidate.currency == "USD" and candidate.rate_basis is Basis.HOURLY


def test_twelve_rows_cannot_hide_duplicate_and_missing_month(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    configure(monkeypatch, tmp_path, [*range(1, 12), 11])
    with pytest.raises(ValueError, match="duplicate monthly"):
        extractor.main()
    assert not extractor.OUT.exists()


def test_incomplete_fred_calendar_is_omitted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extractor, "START_YEAR", 1950)
    monkeypatch.setattr(extractor, "END_YEAR", 1950)
    assert extractor._annualize({1950: {month: 1.3158 for month in range(1, 12)}}) == {}
