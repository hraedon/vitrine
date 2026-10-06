"""Lead checkpoints preserve the table's population, statistic and sample periods.

The transcription audit owns numeric extraction. These regressions guard the
other way this exhibit could lie: changing ages/statistics, collapsing repeated
decade records, or representing sampling windows as annual observations.
"""

from __future__ import annotations

from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from vitrine.loader import load_corpus
from vitrine.model import Corpus
from vitrine.series import load_series
from vitrine.site import curation, svg
from vitrine.site.curation.checkpoints import CHECKPOINT_ARCS
from vitrine.site.projections.checkpoints import checkpoint_points, checkpoint_sections
from vitrine.site.projections.corridors import (
    _build_wings,
    project_corridor,
    validate_comparative_registries,
)
from vitrine.site.projections.facts import index_facts

DATA = Path(__file__).parent.parent / "data"
ARC = CHECKPOINT_ARCS[0]
PERIODS = (
    "1976–1980", "1988–1994", "1999–2002", "2003–2006", "2007–2010",
    "2013–2016", "2017–March 2020",
)


@pytest.fixture(scope="module")
def corpus() -> Corpus:
    return load_corpus(DATA)


def _changed_fact(corpus: Corpus, **changes: object) -> Corpus:
    fact_id = ARC.checkpoints[0].fact_id
    rooms = tuple(
        replace(room, facts=tuple(
            replace(fact, **changes) if fact.id == fact_id else fact
            for fact in room.facts
        ))
        for room in corpus.rooms
    )
    return replace(corpus, rooms=rooms)


def test_periods_are_explicit_and_do_not_collapse_into_decades(corpus: Corpus) -> None:
    points = checkpoint_points(corpus, index_facts(corpus), ARC)
    assert tuple(point.period for point in points) == PERIODS
    assert len(points) == len({point.fact_id for point in points}) == 7
    assert sum(point.fact_id.startswith("us-2000s-") for point in points) == 2
    assert sum(point.fact_id.startswith("us-2010s-") for point in points) == 2
    assert ARC.slug not in curation.ARC_BY_SLUG
    assert all("blood-lead" not in series_id for series_id in load_series(DATA))
    assert all(index_facts(corpus)[point.fact_id].fact.price_year is None for point in points)


@pytest.mark.parametrize("changes", [
    {"source": "a-different-survey"},
    {"unit": "µg/dL (geometric mean; children ages 1–5)"},
    {"label": "Geometric mean blood lead, children ages 1–5, 1976–1980"},
    {"label": "Median blood lead, children ages 6–11, 1976–1980"},
    {"label": "Median blood lead, children ages 1–5, 1976"},
    {"quantity": None},
    {"quantity": float("nan")},
    {"quantity": -1.0},
])
def test_incompatible_observations_cannot_become_geometry(
    corpus: Corpus, changes: dict[str, object],
) -> None:
    changed = _changed_fact(corpus, **changes)
    with pytest.raises(ValueError, match="checkpoint fact"):
        checkpoint_points(changed, index_facts(changed), ARC)


@pytest.mark.parametrize("population", [
    "US adults",
    "US hospitalized children ages 1–5",
    "US children ages 1–5 attending selected clinical screening programmes",
])
def test_source_population_change_refuses_the_comparison(
    corpus: Corpus, population: str,
) -> None:
    sources = dict(corpus.sources)
    sources[ARC.source] = replace(sources[ARC.source], population=population)
    changed = replace(corpus, sources=sources)
    with pytest.raises(ValueError, match="source population"):
        checkpoint_points(changed, index_facts(changed), ARC)


def test_missing_fact_and_duplicate_period_refuse_the_comparison(corpus: Corpus) -> None:
    missing = replace(ARC, checkpoints=(replace(ARC.checkpoints[0], fact_id="missing"),))
    with pytest.raises(ValueError, match="unknown or foreign fact"):
        checkpoint_points(corpus, index_facts(corpus), missing)
    duplicate = replace(ARC, checkpoints=(ARC.checkpoints[0], ARC.checkpoints[0]))
    with pytest.raises(ValueError, match="duplicate fact or sampling period"):
        checkpoint_points(corpus, index_facts(corpus), duplicate)


def test_truncating_a_sampling_period_cannot_pass_the_label_binding(corpus: Corpus) -> None:
    truncated = replace(
        ARC, checkpoints=(replace(ARC.checkpoints[-1], period="2017"),),
    )
    with pytest.raises(ValueError, match="period, population or statistic missing"):
        checkpoint_points(corpus, index_facts(corpus), truncated)


def test_chart_is_discrete_and_retains_full_source_labels(corpus: Corpus) -> None:
    section = checkpoint_sections(corpus, index_facts(corpus))[0]
    chart = ET.fromstring(str(section.chart))
    assert section.coverage == "7 sampling periods"
    assert "calendar scale" in chart.attrib["aria-label"]
    assert "equally spaced categories" in " ".join(section.caveats)
    assert chart.findall(".//polyline") == []
    assert all(line.attrib.get("class") == "grid" for line in chart.findall(".//line"))
    assert chart.findall(".//*[@data-series-id]") == []
    marks = chart.findall(".//*[@data-fact-id]")
    assert tuple(mark.attrib["data-sampling-period"] for mark in marks) == PERIODS
    assert len(chart.findall(".//circle")) == 7
    index = index_facts(corpus)
    for mark in marks:
        fact = index[mark.attrib["data-fact-id"]].fact
        assert mark.findtext("text[@class='vlab']") == fact.value
        assert mark.findtext("text[@class='xlab']") in fact.label
    # Irregular sampling windows get equal category slots, not invented dates.
    positions = [float(mark.find("circle").attrib["cx"]) for mark in marks]
    steps = [b - a for a, b in pairwise(positions)]
    assert max(steps) - min(steps) < 0.2


def test_documented_gap_is_never_a_zero_dot(corpus: Corpus) -> None:
    changed = _changed_fact(corpus, value="no reliable record", quantity=None)
    section = checkpoint_sections(changed, index_facts(changed))[0]
    chart = ET.fromstring(str(section.chart))
    first = chart.find(".//*[@data-fact-id]")
    assert first is not None
    assert first.find("circle") is None
    assert first.findtext("text[@class='gaplab']") == "no reliable record"
    assert len(chart.findall(".//circle")) == 6
    assert section.coverage == "6 sampling periods; 1 documented gap"


def test_checkpoint_hit_regions_are_disjoint_and_cover_the_linked_marks(corpus: Corpus) -> None:
    """Interaction columns must not steal neighbouring observations' clicks.

    Browser tests exercise anchor-centre clicks with and without JavaScript;
    these bounds keep transparent hit targets from growing across another link.
    """
    section = checkpoint_sections(corpus, index_facts(corpus))[0]
    chart = ET.fromstring(str(section.chart))
    _, _, width, height = map(float, chart.attrib["viewBox"].split())
    right_edge = 0.0
    for anchor in chart.findall("a"):
        hit = anchor.find("rect[@class='checkpoint-hit']")
        mark = anchor.find("g[@data-fact-id]")
        assert hit is not None and mark is not None
        assert hit.attrib["fill"] == "transparent"
        assert hit.attrib["pointer-events"] == "all"
        assert "data-fact-id" not in hit.attrib
        left, top = float(hit.attrib["x"]), float(hit.attrib["y"])
        right = left + float(hit.attrib["width"])
        bottom = top + float(hit.attrib["height"])
        assert right_edge <= left < right <= width
        assert 0 <= top < bottom <= height
        right_edge = right
        dot = mark.find("circle")
        assert dot is not None
        assert left < float(dot.attrib["cx"]) < right
        assert top < float(dot.attrib["cy"]) < bottom
        for label in mark.findall("text"):
            assert left < float(label.attrib["x"]) < right
            assert top < float(label.attrib["y"]) < bottom


def test_checkpoint_comparison_is_gated_and_has_all_placards(corpus: Corpus) -> None:
    index = index_facts(corpus)
    rooms = [room for room in corpus.rooms if room.country in curation.CURATED_COUNTRIES]
    page = project_corridor(corpus, index, load_series(DATA), rooms, {})
    wing = next(wing for wing in page.wings if wing.slug == "different-country")
    section = next(section for section in wing.arcs if section.slug == ARC.slug)
    assert section.coverage == "7 sampling periods"
    overlay_ids = {ref.fact.id for ref in page.overlay_facts}
    assert {point.fact_id for point in ARC.checkpoints} <= overlay_ids
    validate_comparative_registries(corpus)
    fact_id = ARC.checkpoints[0].fact_id
    changed = replace(corpus, rooms=tuple(
        replace(room, country="zz") if any(fact.id == fact_id for fact in room.facts) else room
        for room in corpus.rooms
    ))
    with pytest.raises(ValueError, match=r"CHECKPOINT_ARCS\[blood-lead-median\]"):
        validate_comparative_registries(changed)


def test_checkpoint_slug_cannot_hide_an_existing_exhibit(corpus: Corpus) -> None:
    section = checkpoint_sections(corpus, index_facts(corpus))[0]
    with pytest.raises(ValueError, match="unique across chart registries"):
        _build_wings((section, section), 0)


def test_checkpoint_markup_escapes_authored_text() -> None:
    point = svg.CheckpointPoint(
        fact_id="f", period="1976–1980 <", label='Median < " &',
        value="1.0 & µg/dL", quantity=1.0, tier="A",
    )
    chart = ET.fromstring(svg.checkpoint_chart((point,), "µg/dL", point.label))
    assert chart.findtext(".//text[@class='xlab']") == point.period
    assert chart.findtext(".//text[@class='vlab']") == point.value
