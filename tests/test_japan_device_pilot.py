"""A focused equipment route enrolls the country, not every room's status."""

import re
from html import unescape
from itertools import combinations
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.model import Corpus
from vitrine.series import load_series
from vitrine.site import curation
from vitrine.site.build import build_site
from vitrine.site.curation.collections import HOUSE_ROOMS, EditorialStatus, editorial_choice
from vitrine.site.projections.rooms import room_story

DATA = Path(__file__).parent.parent / "data"
DEVICE_IDS = (
    "jp-1990s-pc",
    "jp-1990s-mobile-phone",
    "jp-1990s-fax",
    "jp-1990s-word-processor",
)
RESEARCH_DECADES = ("1950s", "1960s", "1970s", "1980s", "2000s", "2010s")


@pytest.fixture(scope="module")
def corpus() -> Corpus:
    return load_corpus(DATA)


@pytest.fixture(scope="module")
def site(corpus: Corpus, tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("japan-device-pilot")
    build_site(corpus, out, load_series(DATA), DATA)
    return out


def test_device_room_is_the_only_focused_japan_route(corpus: Corpus) -> None:
    room = next(room for room in corpus.rooms if room.slug == "jp-1990s")
    assert editorial_choice(room.slug).status is EditorialStatus.FOCUSED
    story = room_story(room)
    assert story is not None
    assert tuple(fact.id for fact in story.facts) == DEVICE_IDS
    assert all(fact.source == "jp-nsfiie" and "1999" in fact.label for fact in story.facts)
    assert not any(character.isdigit() for character in story.title + story.question)
    assert {story.slug for story in curation.ROOM_STORIES if story.country == "jp"} == {
        room.slug,
    }


def test_device_route_is_visible_and_keeps_each_source_card(corpus: Corpus, site: Path) -> None:
    html = unescape((site / "rooms/jp-1990s.html").read_text())
    assert '<section class="room-overture"' in html
    assert "Equipment through a household survey" in html
    assert "Focused exhibit" in html
    stops = re.findall(
        r'<a class="story-stop" href="#([^"]+)--modal" data-fact-id="([^"]+)"', html,
    )
    assert stops == [(fact_id, fact_id) for fact_id in DEVICE_IDS]
    room = next(room for room in corpus.rooms if room.slug == "jp-1990s")
    facts = {fact.id: fact for fact in room.facts}
    source = corpus.sources["jp-nsfiie"]
    for fact_id in DEVICE_IDS:
        fact = facts[fact_id]
        overlay = html.split(f'id="{fact_id}--modal"', 1)[1].split(
            '<div class="placard-overlay"', 1,
        )[0]
        assert fact.value in overlay
        assert fact.label in overlay
        assert source.population in overlay
        assert f'href="{source.url}"' in overlay
    assert "do not establish" in html
    assert "same household" in html
    assert "device use" in html
    assert "matched household" in html


@pytest.mark.parametrize("decade", RESEARCH_DECADES)
def test_other_japan_rooms_keep_research_status_without_hidden_stories(
    corpus: Corpus, site: Path, decade: str,
) -> None:
    room = next(room for room in corpus.rooms if room.slug == f"jp-{decade}")
    assert editorial_choice(room.slug).status is EditorialStatus.RESEARCH
    assert room_story(room) is None
    html = (site / "rooms" / f"{room.slug}.html").read_text()
    assert "Research holding" in html
    assert 'class="story-stop"' not in html
    if decade == "1950s":
        assert editorial_choice(room.slug).rationale == (
            "A few records, an unfinished picture: the household-income and "
            "workplace-wage observations describe separate populations. The remaining "
            "panels are documented research gaps, not evidence of historical absence."
        )


def test_country_enrollment_adds_every_japan_lobby_row(corpus: Corpus, site: Path) -> None:
    assert "jp" in curation.CURATED_COUNTRIES
    lobby = (site / "index.html").read_text()
    labels = re.findall(r">JP (\d{4}s)</a>", lobby)
    assert len(labels) == len(set(labels)) == 7
    assert set(labels) == {room.decade for room in corpus.rooms if room.country == "jp"}
    for decade in labels:
        assert f'href="rooms/jp-{decade}.html"' in lobby


def test_japan_entrance_explains_and_links_the_limited_route(site: Path) -> None:
    html = (site / "collections/japan.html").read_text()
    assert 'href="../rooms/jp-1990s.html#room-story-title"' in html
    assert "Open the 1990s equipment route" in html
    assert "other decade rooms remain research holdings" in html
    assert "These folders are research holdings" not in html


def test_enrollment_keeps_us_comparisons_and_house_scope(corpus: Corpus, site: Path) -> None:
    assert set(curation.COMPARATIVE_COUNTRIES) == {"us"}
    jp_rooms = [room for room in corpus.rooms if room.country == "jp"]
    assert all(room.slug not in HOUSE_ROOMS for room in jp_rooms)
    for room in jp_rooms:
        html = (site / "rooms" / f"{room.slug}.html").read_text()
        assert '<section class="house-experience"' not in html
        assert "See this metric across all decades" not in html
    us_rooms = [room for room in corpus.rooms if room.country == "us"]
    pairs = list((site / "corridors").glob("*--*.html"))
    assert len(pairs) == len(us_rooms) * (len(us_rooms) - 1) // 2
    expected_pairs = {
        f"{a}--{b}.html" for a, b in combinations(sorted(room.decade for room in us_rooms), 2)
    }
    assert {page.name for page in pairs} == expected_pairs
    assert all(
        'data-fact-id="jp-' not in page.read_text() for page in pairs
    )
    for relative in ("corridors/index.html", "walkthrough.html", "affordability/index.html"):
        assert 'data-fact-id="jp-' not in (site / relative).read_text()
