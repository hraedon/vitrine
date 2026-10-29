"""Compound verification checks actual source fields, periods and publisher formats."""

import json
from pathlib import Path

import pytest
from middle_us_health_food_review import cms_value, extract, farm_row, qualify


def test_source_dash_cannot_become_a_measured_zero() -> None:
    assert cms_value({"year": "1960", "medicare": None}, "medicare") == (
        "Not reported for 1960 — the source prints a dash"
    )


def test_gdp_comparison_reads_both_source_endpoints() -> None:
    current = {"year": "2024", "gdp_share": "18"}
    baseline = {"year": "1960", "gdp_share": "5"}
    assert cms_value(current, "gdp-share-arc", baseline) == "5.0% (1960) → 18.0% (2024)"
    baseline["gdp_share"] = "6"
    assert cms_value(current, "gdp-share-arc", baseline) == "6.0% (1960) → 18.0% (2024)"
    with pytest.raises(ValueError, match="original 1960 baseline"):
        cms_value(current, "gdp-share-arc")


def _fruit_books():
    openpyxl = pytest.importorskip("openpyxl")
    book, cache = openpyxl.Workbook(), openpyxl.Workbook()
    sheet, cached = book.active, cache.active
    assert sheet is not None and cached is not None
    for address, value in {
        "A7": 1970, "B7": 205.052, "C7": 91.4, "D7": 2.3, "E7": "=C7+D7",
        "F7": 1, "G7": "NA", "H7": "=E7-F7", "I7": "=IF(H7=0,0,IF(B7=0,0,H7/B7))",
    }.items():
        sheet[address] = value
    sheet["I7"].number_format = "#,##0.0"
    cached["I7"] = 92.7 / 205.052
    return sheet, cached


def test_fruit_uses_published_precision_instead_of_hidden_cache_digits() -> None:
    sheet, cached = _fruit_books()
    result = farm_row(sheet, cached, 7, True)
    assert result["value"] == "0.5"
    assert result["precision"] == 1
    assert result["food_million_pounds"] == "92.7"
    assert result["population_millions"] == "205.052"


def test_cache_and_uninspected_formulas_are_refused() -> None:
    sheet, cached = _fruit_books()
    cached["I7"] = 0.5
    with pytest.raises(ValueError, match="cache does not reproduce"):
        farm_row(sheet, cached, 7, True)
    sheet, cached = _fruit_books()
    sheet["I7"] = "=H7/B7*0.94"
    with pytest.raises(ValueError, match="farm-weight ratio"):
        farm_row(sheet, cached, 7, True)
    sheet, cached = _fruit_books()
    sheet["C7"] = "=100-8.6"
    with pytest.raises(ValueError, match="literal supply/use"):
        farm_row(sheet, cached, 7, True)


def test_original_sources_reproduce_artifact_and_all_compound_records() -> None:
    root = Path(__file__).parent.parent
    artifact = root / "samples/remaining-audit-20261028/middle-us-health-food.json"
    if not artifact.is_file():
        pytest.skip("original CMS/ERS archive required")
    pytest.importorskip("openpyxl")
    result = extract(root / "samples")
    assert result == json.loads(artifact.read_text(encoding="utf-8"))
    qualify(result, root / "data")
