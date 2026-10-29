"""An archived number is not permission to reuse it on an excluded axis."""

from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.site import curation, svg
from vitrine.site.curation.models import Metric
from vitrine.site.projections.arcs import arc_points
from vitrine.site.projections.chart_tables import metric_tables, point_table
from vitrine.site.projections.corridors import _build_comp_rows
from vitrine.site.projections.facts import FactRef, index_facts
from vitrine.site.projections.metrics import metric_markers
from vitrine.site.projections.pairs import pair_families, project_pair
from vitrine.site.projections.stage import build_stage
from vitrine.site.projections.walkthrough import _build_metrics


@pytest.fixture(scope="module")
def index() -> dict[str, FactRef]:
    return index_facts(load_corpus(Path(__file__).parent.parent / "data"))


def test_food_record_from_later_survey_is_archived_but_not_a_1950s_point(
    index: dict[str, FactRef],
) -> None:
    arc = curation.ARC_BY_SLUG["food-share"]
    fact_id = arc.fact_ids["1950s"]
    assert "$1,309" in index[fact_id].fact.value  # Archived annual expense, not a share.
    point = next(point for point in arc_points(index, arc, "../") if point.decade == "1950s")
    assert point.fact_id == fact_id and point.quantity is None
    table = point_table((point,), arc.unit)
    assert table.rows[0].value == "Not plotted"
    assert table.rows[0].href == f"#{fact_id}--modal"
    assert "1950s" not in curation.STAGE_BY_COUNTRY["us"].food_share
    stage = build_stage(index[fact_id].room, index, "../")
    assert all(note.fact_id != fact_id for note in stage.zone_notes)
    pair = next(family for family in pair_families(index, "1950s", "1980s", "../")
                if family.label == arc.label)
    assert pair.cells[0].gap and not pair.cells[1].gap
    assert "not comparable" in pair.cells[0].text
    walkthrough = next(metric for metric in _build_metrics(index, []) if metric.label == arc.label)
    cell = next(cell for cell in walkthrough.cells if cell.decade == "1950s")
    assert cell.fact_id == fact_id and cell.gap and cell.bar == 0


def test_all_arc_exclusions_propagate_to_direct_metrics_and_pair_cells(
    index: dict[str, FactRef],
) -> None:
    for arc in curation.ARCS:
        if not arc.plot_gaps:
            continue
        markers = metric_markers(Metric("test", arc.label, arc.unit, "", source_arc=arc.slug),
                                 index, "../")
        for decade in arc.plot_gaps:
            fact_id = arc.fact_ids[decade]
            marker = next(marker for marker in markers if marker.fact_id == fact_id)
            assert marker.quantity is None, (arc.slug, fact_id)
            other = next(candidate for candidate in arc.fact_ids if candidate != decade)
            pair = next(family for family in pair_families(index, decade, other, "../")
                        if family.label == arc.label)
            assert pair.cells[0].gap and pair.cells[0].fact_id == fact_id


@pytest.mark.parametrize("slug,decade", [
    ("infant-mortality", "2020s"),  # Source uses a per-100,000 denominator.
    ("internet", "2020s"),  # Adults using internet are not connected households.
    ("cancer-survival", "1960s"),  # White ACS estimate is not the SEER cohort.
    ("television", "1940s"),  # Published household count is not a percentage.
    ("plumbing", "1940s"),  # Private bath/toilet is not complete plumbing.
])
def test_reviewed_measurement_seams_remain_linked_exclusions(
    index: dict[str, FactRef], slug: str, decade: str,
) -> None:
    arc = curation.ARC_BY_SLUG[slug]
    point = next(point for point in arc_points(index, arc, "../") if point.decade == decade)
    assert point.quantity is None
    assert point.fact_id == arc.fact_ids[decade]


def test_daily_unpaid_hours_never_acquire_weekly_walkthrough_geometry(
    index: dict[str, FactRef], monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(curation, "WALKTHROUGH_STOPS", ("1900s", "2010s"))
    arc = curation.ARC_BY_SLUG["home-production-women"]
    walkthrough = next(metric for metric in _build_metrics(index, []) if metric.label == arc.label)
    cell = next(cell for cell in walkthrough.cells if cell.decade == "2010s")
    assert index[cell.fact_id].fact.quantity is not None
    assert cell.gap and cell.bar == 0 and "not comparable" in cell.text


def test_excluded_diffusion_quantity_is_only_a_source_link_on_the_house(
    index: dict[str, FactRef],
) -> None:
    fact_id = "us-2020s-phone-vehicle-diffusion"
    stage = build_stage(index[fact_id].room, index, "../")
    artifact = next(artifact for artifact in stage.artifacts if artifact.fact_id == fact_id)
    assert artifact.quantity is None


def test_metric_table_period_never_promotes_midpoint_to_observation_year(
    index: dict[str, FactRef],
) -> None:
    metric = curation.METRIC_BY_SLUG["food-share"]
    markers = metric_markers(metric, index, "../")
    marker = next(marker for marker in markers if marker.fact_id == "us-1990s-food-basket")
    assert marker.year == 1995 and marker.approximate_position
    assert marker.period == "1990s" and "1996" in marker.label
    table, = metric_tables(metric, {}, markers, {}, "../")
    row = next(row for row in table.rows if row.label == marker.label)
    assert row.period == "1990s" and row.period != str(marker.year)
    assert "illustrative" in table.note
    chart = svg.affordability_chart({}, (), metric.unit, markers=(marker,))
    assert "1990s (illustrative decade position)" in chart


def test_withdrawn_1970s_shares_are_linked_gaps_in_every_consumer(
    index: dict[str, FactRef],
) -> None:
    corpus = load_corpus(Path(__file__).parent.parent / "data")
    budget_id = "us-1970s-expenditure-shares"
    apparel_id = "us-1970s-cex-apparel-share"
    for fact_id in (budget_id, apparel_id):
        fact = index[fact_id].fact
        assert fact.quantity is None and fact.value.startswith("no reliable record")
    comp = next(row for row in _build_comp_rows(index, "../") if row.decade == "1970s")
    assert comp.gap and not comp.segments and not comp.bar and comp.fact_id == budget_id
    pair = project_pair(corpus, index, "1970s", "1980s", {})
    assert next(row for row in pair.comp_rows if row.decade == "1970s").gap
    apparel = next(family for family in pair.families
                   if any(cell.fact_id == apparel_id for cell in family.cells))
    assert next(cell for cell in apparel.cells if cell.fact_id == apparel_id).gap
    food = next(family for family in pair.families
                if family.label == curation.ARC_BY_SLUG["food-share"].label)
    cell = next(cell for cell in food.cells if cell.decade == "1970s")
    assert cell.gap and "no comparable value" in cell.text
    assert "$" not in cell.text  # No nominal food expense under a percentage axis.
    stage = build_stage(index[budget_id].room, index, "../")
    assert all(note.fact_id not in {budget_id, "us-1970s-food-basket"}
               for note in stage.zone_notes)
