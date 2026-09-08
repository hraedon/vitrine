"""Editorial routes cannot infer dates, borrow populations, or erase archives."""

import re
from dataclasses import replace
from html import unescape
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.model import Corpus
from vitrine.series import load_series
from vitrine.site.build import build_site
from vitrine.site.curation.collections import (
    JAPAN_THEMES,
    EditorialStatus,
    editorial_choice,
)
from vitrine.site.projections.collections import observation_year, project_japan_collection
from vitrine.site.projections.facts import index_facts
from vitrine.site.projections.rooms import project_room

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def corpus() -> Corpus:
    return load_corpus(DATA)


@pytest.fixture(scope="module")
def site(corpus: Corpus, tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("collection-site")
    build_site(corpus, out, load_series(DATA), DATA)
    return out


def test_editorial_status_does_not_follow_density_or_country(corpus: Corpus) -> None:
    index = index_facts(corpus)
    for slug in ("jp-2010s", "us-1910s"):
        room = next(r for r in corpus.rooms if r.slug == slug)
        assert len(room.facts) > 8  # old density threshold is not the decision
        page = project_room(corpus, room, (room,), 1, index, {})
        assert page.compact
        assert page.editorial.status is EditorialStatus.RESEARCH
    assert editorial_choice("us-1950s").status is EditorialStatus.GUIDED
    assert editorial_choice("us-1940s").status is EditorialStatus.FOCUSED
    assert editorial_choice("us-2030s").status is EditorialStatus.RESEARCH


def test_primary_us_object_gallery_leaves_compound_records_in_the_archive(site: Path) -> None:
    html = (site / "rooms" / "us-1950s.html").read_text()
    gallery_marks = set(re.findall(
        r'<a class="artifact-card"[^>]*data-fact-id="([^"]+)"', html,
    ))
    assert "us-1950s-tv-diffusion" in gallery_marks
    for fact_id in ("us-1950s-telephone-automobile", "us-1950s-food-basket"):
        assert fact_id not in gallery_marks
        assert f'id="{fact_id}"' in html
        assert f'id="{fact_id}--modal"' in html


def test_japan_selections_preserve_observation_dates_and_population(corpus: Corpus) -> None:
    page = project_japan_collection(corpus)
    all_ids = []
    for theme in page.themes:
        for lens in theme.lenses:
            assert lens.observations
            assert lens.note
            for item in lens.observations:
                assert item.ref.room.country == "jp"
                assert item.ref.fact.source == lens.source.id
                assert str(item.year) in item.ref.fact.label
                all_ids.append(item.ref.fact.id)
    assert len(all_ids) == len(set(all_ids)) == len(page.overlay_facts)
    television = next(
        item for theme in page.themes for lens in theme.lenses
        for item in lens.observations if item.ref.fact.id == "jp-2010s-flat-tv"
    )
    assert television.year == 2009
    assert television.outside_decade


@pytest.mark.parametrize("failure", ["source", "duplicate", "gap", "missing"])
def test_bad_collection_selections_fail(corpus: Corpus, failure: str) -> None:
    theme = JAPAN_THEMES[0]
    lens = theme.lenses[0]
    if failure == "source":
        lens = replace(lens, source="jp-mls")
    elif failure == "duplicate":
        lens = replace(lens, fact_ids=(lens.fact_ids[0], lens.fact_ids[0]))
    elif failure == "gap":
        lens = replace(lens, fact_ids=("jp-1950s-table-gap",))
    else:
        lens = replace(lens, fact_ids=("jp-1950s-not-a-record",))
    with pytest.raises(ValueError):
        project_japan_collection(corpus, (replace(theme, lenses=(lens,)),))


def test_undated_or_ambiguous_observation_cannot_borrow_room_year(corpus: Corpus) -> None:
    fact = index_facts(corpus)["jp-1950s-fies-workers-income"].fact
    with pytest.raises(ValueError, match="observation year"):
        observation_year(replace(fact, label="Monthly household income"))
    with pytest.raises(ValueError, match="observation year"):
        observation_year(replace(fact, label="Monthly household income, 1955 and 1965"))
    with pytest.raises(ValueError, match="disagree"):
        observation_year(replace(fact, price_year=1965))


def test_japan_page_keeps_disclaimer_source_cards_and_decade_archive(
    corpus: Corpus, site: Path,
) -> None:
    page = project_japan_collection(corpus)
    html = unescape((site / "collections" / "japan.html").read_text())
    assert corpus.assumptions["composite-family"].statement in html
    assert "Observed 2009" in html
    assert "Filed in the 2010s archive" in html
    assert "not a four-person median" in html
    for ref in page.overlay_facts:
        assert f'id="{ref.fact.id}--modal"' in html
        assert f'../rooms/{ref.room.slug}.html#{ref.fact.id}' in html
        assert corpus.sources[ref.fact.source].population in html
    for room in page.rooms:
        decade = (site / "rooms" / f"{room.slug}.html").read_text()
        assert "../collections/japan.html" in decade
        for fact in room.facts:
            assert f'id="{fact.id}"' in decade
    assert 'href="collections/japan.html"' in (site / "index.html").read_text()
