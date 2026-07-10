"""The affordability dashboard (Plan 011): metric computation, recession
loading, and the chart renderer. Metrics are computed ratios — the tests pin
the computation, not authored values."""

from pathlib import Path

from vitrine.model import Tier
from vitrine.series import Series
from vitrine.site import curation, svg
from vitrine.site.render import (
    _load_recessions,
    _resolve_metric,
    _series_numeric,
)


def _series(sid: str, values: dict[int, float] | None = None,
            values_minor: dict[int, int] | None = None) -> Series:
    return Series(
        id=sid, label="L", source="src", tier=Tier.A,
        unit="u", population="p",
        values=values or {}, values_minor=values_minor or {},
    )


# ── canonical-unit conversion ────────────────────────────────────────────────


def test_series_numeric_converts_monetary_cents_to_dollars() -> None:
    assert _series_numeric(_series("s", values_minor={1950: 331900}))[1950] == 3319.0


def test_series_numeric_keeps_float_series_as_is() -> None:
    assert _series_numeric(_series("s", values={1950: 24.1}))[1950] == 24.1


# ── metric resolution (ratio mode) ───────────────────────────────────────────


def test_ratio_metric_intersects_years_and_divides() -> None:
    series = {
        "num": _series("num", values_minor={1950: 100000, 1960: 200000}),  # $1000,$2000
        "den": _series("den", values_minor={1950: 50000, 1970: 60000}),    # $500,$600
    }
    metric = curation.Metric("m", "M", "u", "cap",
                             numerator=("num",), denominator=("den",))
    vals, note = _resolve_metric(metric, series)
    assert note == ""
    assert set(vals) == {1950}  # only the intersection year
    assert vals[1950] == 2.0     # 1000 / 500


def test_ratio_metric_applies_numerator_scale() -> None:
    series = {
        "num": _series("num", values={1950: 50.0}),   # $50/week
        "den": _series("den", values_minor={1950: 2600000}),  # $26000/yr
    }
    metric = curation.Metric("m", "M", "u", "cap",
                             numerator=("num",), denominator=("den",),
                             numerator_scale=52.0, percent=True)
    vals, _ = _resolve_metric(metric, series)
    # 50 * 52 / 26000 * 100 = 10.0
    assert vals[1950] == 10.0


def test_base_year_normalizes_to_index_100() -> None:
    series = {
        "num": _series("num", values={1964: 2.5, 2024: 30.0}),
        "den": _series("den", values={1964: 31.0, 2024: 314.0}),
    }
    metric = curation.Metric("m", "M", "u", "cap",
                             numerator=("num",), denominator=("den",),
                             base_year=2024)
    vals, _ = _resolve_metric(metric, series)
    assert abs(vals[2024] - 100.0) < 1e-9
    # 1964 ratio = 2.5/31 = 0.0806; 2024 ratio = 30/314 = 0.0955
    # index[1964] = 0.0806/0.0955*100 ≈ 84.4
    assert 83 < vals[1964] < 86


def test_metric_reports_when_series_missing() -> None:
    metric = curation.Metric("m", "M", "u", "cap",
                             numerator=("no-such",), denominator=("den",))
    vals, note = _resolve_metric(metric, {"den": _series("den", values={1950: 1.0})})
    assert vals == {}
    assert "not found" in note


def test_metric_reports_when_no_overlap() -> None:
    series = {
        "num": _series("num", values={1950: 1.0}),
        "den": _series("den", values={1970: 1.0}),
    }
    metric = curation.Metric("m", "M", "u", "cap",
                             numerator=("num",), denominator=("den",))
    vals, note = _resolve_metric(metric, series)
    assert vals == {}
    assert "no years" in note


def test_direct_mode_metric_returns_empty_values() -> None:
    metric = curation.Metric("m", "M", "u", "cap", source_arc="food-share")
    vals, note = _resolve_metric(metric, {})
    assert vals == {}
    assert note == ""  # markers carry the data, not the resolver


# ── merged numerator (home value splice across two series) ───────────────────


def test_merged_numerator_unions_years_across_series() -> None:
    series = {
        "dec": _series("dec", values_minor={1950: 735400, 1960: 1190000}),
        "acs": _series("acs", values_minor={2024: 36060000}),
        "inc": _series("inc", values_minor={1950: 33190000, 1960: 56000000, 2024: 105800000}),
    }
    metric = curation.Metric("m", "M", "u", "cap",
                             numerator=("dec", "acs"), denominator=("inc",))
    vals, _ = _resolve_metric(metric, series)
    assert set(vals) == {1950, 1960, 2024}


# ── committed dashboard ──────────────────────────────────────────────────────


def test_committed_metrics_all_resolve_or_have_markers() -> None:
    """Every dashboard metric must produce annual values OR direct-mode markers
    — no metric ships as an empty chart."""
    from vitrine.loader import load_corpus
    from vitrine.site.render import _index_facts, _metric_markers
    data = Path(__file__).parent.parent / "data"
    corpus = load_corpus(data)
    from vitrine.series import load_series
    series = load_series(data)
    index = _index_facts(corpus)
    for metric in curation.AFFORDABILITY_METRICS:
        vals, note = _resolve_metric(metric, series)
        markers = _metric_markers(metric, index, "")
        assert vals or markers, (
            f"metric {metric.slug!r} renders neither values nor markers ({note})"
        )


# ── recession loading ────────────────────────────────────────────────────────


def test_load_recessions_parses_committed_file() -> None:
    data = Path(__file__).parent.parent / "data"
    bands, url = _load_recessions(data / "recessions.toml")
    assert len(bands) >= 18  # NBER cycles peak >= 1900
    assert "nber.org" in url
    # the Great Depression: Aug 1929 → Mar 1933
    gd = [b for b in bands if 1929 < b.peak < 1930]
    assert gd, "Great Depression recession (1929) must be present"
    assert abs(gd[0].trough - 1933.167) < 0.01  # Mar 1933 ≈ 1933.167


def test_load_recessions_missing_file_is_empty() -> None:
    bands, url = _load_recessions(Path("/nonexistent/recessions.toml"))
    assert bands == ()
    assert url == ""


# ── chart renderer ───────────────────────────────────────────────────────────


def test_affordability_chart_emits_metric_marks_not_fact_ids() -> None:
    """Ratio-metric points are computed (data-metric-id), never facts."""
    chart = svg.affordability_chart(
        {1964: 85.0, 2024: 100.0}, (), "index", metric_slug="real-wage"
    )
    assert 'data-metric-id="real-wage"' in chart
    assert "data-fact-id" not in chart  # ratio points are not facts


def test_affordability_chart_recession_bands_carry_no_fact_id() -> None:
    """Recession bands are annotation — provenance via the footer, not a fact."""
    recs = (svg.Recession(peak=1973.92, trough=1975.17),)
    chart = svg.affordability_chart({1970: 90.0, 1980: 78.0}, recs, "idx")
    assert 'class="recession"' in chart
    assert "data-fact-id" not in chart.split('<rect class="recession"')[1].split('/>')[0]


def test_affordability_chart_empty_values_returns_empty() -> None:
    assert svg.affordability_chart({}, (), "u") == ""


def test_direct_mode_markers_form_a_visible_trajectory() -> None:
    markers = (
        svg.MetricMarker(1950, "f-1", "#f-1", "A", "Food", "30%", 30.0),
        svg.MetricMarker(1960, "f-2", "#f-2", "A", "Food", "25%", 25.0),
    )
    chart = svg.affordability_chart({}, (), "%", markers=markers)
    assert 'class="join direct-series"' in chart
    assert 'data-fact-id="f-1"' in chart
    assert 'data-fact-id="f-2"' in chart


def test_index_chart_can_use_a_nonzero_baseline() -> None:
    chart = svg.affordability_chart(
        {1964: 80.0, 2024: 100.0},
        (),
        "index",
        zero_baseline=False,
    )
    assert 'class="ylab"' in chart
    assert '>0</text>' not in chart


def test_annual_series_line_breaks_at_missing_year() -> None:
    chart = svg.arc_chart_series(
        {2000: 10.0, 2001: 11.0, 2003: 13.0, 2004: 14.0},
        (),
        "units",
    )
    assert chart.count('class="series-line"') == 2


def test_nice_axis_rounding_does_not_discard_half_the_plot() -> None:
    assert svg._nice_axis_top(46.8) == 50.0
    assert svg._nice_axis_top(91.5) == 100.0
