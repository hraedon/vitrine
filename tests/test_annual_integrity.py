"""Annual series preserve finite values, currency boundaries and real gaps."""

from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from xml.etree import ElementTree

import pytest

from vitrine.check import check_series
from vitrine.loader import load_corpus
from vitrine.model import Tier
from vitrine.series import Series, SeriesError, load_series
from vitrine.site import curation, svg
from vitrine.site.projections.metrics import resolve_metric

DATA = Path(__file__).parent.parent / "data"


@pytest.mark.parametrize("literal", ["nan", "+nan", "-nan", "inf", "+inf", "-inf"])
def test_series_loader_rejects_nonfinite_observations(tmp_path: Path, literal: str) -> None:
    directory = tmp_path / "series"
    directory.mkdir()
    (directory / "invalid.toml").write_text(
        '[[series]]\nid = "invalid"\nlabel = "Invalid"\nsource = "test"\n'
        'tier = "A"\nunit = "index"\npopulation = "test"\n'
        f"[series.values]\n1950 = {literal}\n"
    )
    with pytest.raises(SeriesError, match=r"values.*1950.*finite"):
        load_series(tmp_path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_series_gate_rejects_nonfinite_programmatic_observations(value: float) -> None:
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    original = series["cpi-u"]
    values = dict(original.values)
    values[min(values)] = value
    series[original.id] = replace(original, values=values)
    problems = check_series(series, corpus)
    assert any("cpi-u" in problem and "finite" in problem for problem in problems)


def _monetary(sid: str, currency: str, year: int = 1950) -> Series:
    return Series(
        id=sid, label=sid, source="test", tier=Tier.A, unit=currency,
        population="test", values_minor={year: 10000}, currency=currency,
    )


@pytest.mark.parametrize("other_currency", ["GBP", "JPY"])
def test_annual_metric_rejects_cross_currency_division(other_currency: str) -> None:
    series = {"num": _monetary("num", "USD"), "den": _monetary("den", other_currency)}
    metric = curation.Metric("test", "Test", "ratio", "caption",
                             numerator=("num",), denominator=("den",))
    with pytest.raises(ValueError, match="currency mismatch"):
        resolve_metric(metric, series)


def test_annual_metric_rejects_cross_currency_numerator_chain() -> None:
    series = {
        "early": _monetary("early", "USD"),
        "late": _monetary("late", "GBP", 1960),
        "den": _monetary("den", "USD"),
    }
    metric = curation.Metric("test", "Test", "ratio", "caption",
                             numerator=("early", "late"), denominator=("den",))
    with pytest.raises(ValueError, match="currency mismatch"):
        resolve_metric(metric, series)


def test_annual_metric_preserves_same_currency_ratios_and_index_deflation() -> None:
    series = {"num": _monetary("num", "JPY"), "den": _monetary("den", "JPY")}
    metric = curation.Metric("test", "Test", "ratio", "caption",
                             numerator=("num",), denominator=("den",))
    assert resolve_metric(metric, series) == ({1950: 1.0}, "")
    series["den"] = replace(series["den"], currency="", values_minor={}, values={1950: 100})
    assert resolve_metric(metric, series) == ({1950: 100.0}, "")


def test_annual_metric_rejects_overlapping_denominator_observations() -> None:
    series = {
        "num": _monetary("num", "USD"),
        "first": _monetary("first", "USD"),
        "second": replace(_monetary("second", "USD"), values_minor={1950: 20000}),
    }
    metric = curation.Metric("test", "Test", "ratio", "caption",
                             numerator=("num",), denominator=("first", "second"))
    values, note = resolve_metric(metric, series)
    assert values == {}
    assert "denominator series 'second' overlaps [1950]" in note
    assert "merge is ambiguous" in note


def test_annual_metric_preserves_disjoint_denominator_observations() -> None:
    series = {
        "num": replace(_monetary("num", "USD"), values_minor={1950: 10000, 1960: 30000}),
        "first": _monetary("first", "USD"),
        "second": replace(_monetary("second", "USD", 1960), values_minor={1960: 20000}),
    }
    metric = curation.Metric("test", "Test", "ratio", "caption",
                             numerator=("num",), denominator=("first", "second"))
    assert resolve_metric(metric, series) == ({1950: 1.0, 1960: 1.5}, "")


def test_affordability_line_connects_only_consecutive_years() -> None:
    chart = ElementTree.fromstring(svg.affordability_chart(
        {1950: 2.0, 1960: 3.0, 1961: 4.0, 1970: 5.0, 1971: 6.0}, (), "ratio",
        metric_slug="test",
    ))
    dots = chart.findall("circle")
    coordinates = [f"{dot.attrib['cx']},{dot.attrib['cy']}" for dot in dots]
    lines = chart.findall("polyline")
    assert [line.attrib["points"] for line in lines] == [
        " ".join(coordinates[1:3]), " ".join(coordinates[3:5]),
    ]
    assert len(dots) == 5


def test_committed_sparse_affordability_metrics_do_not_bridge_missing_years() -> None:
    series = load_series(DATA)
    for slug in ("home-as-income-years", "car-as-hours-of-work"):
        values, note = resolve_metric(curation.METRIC_BY_SLUG[slug], series)
        assert values and not note
        chart = ElementTree.fromstring(svg.affordability_chart(values, (), "ratio"))
        year_by_coordinate = {
            f"{dot.attrib['cx']},{dot.attrib['cy']}": year
            for year, dot in zip(sorted(values), chart.findall("circle"), strict=True)
        }
        for line in chart.findall("polyline"):
            years = [year_by_coordinate[point] for point in line.attrib["points"].split()]
            assert all(b == a + 1 for a, b in pairwise(years))
        assert len(chart.findall("circle")) == len(values)
