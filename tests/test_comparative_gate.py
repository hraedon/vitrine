"""The comparative layer is decade-keyed US curation — FWI-004 / FWI-005.

Three registries reach across decades to compare rooms: the corridor atlas,
the pair matrix and the affordability dashboard. All are keyed by decade
alone and hold US fact ids, so they are only well-defined inside one wing.
Today that holds because they are projected over ``CURATED_COUNTRIES``; these
tests are the mechanism that reddens when it stops holding, and the
regression guard for the room-level link that reached for them regardless.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.model import Corpus, Fact, Panel, Room, Tier
from vitrine.series import load_series
from vitrine.site import curation
from vitrine.site.projections.affordability import afford_fact_ids
from vitrine.site.projections.corridors import validate_comparative_registries
from vitrine.site.render import render_site

DATA = Path(__file__).parent.parent / "data"

PANEL_LINK = "See this metric across all decades"


# ── FWI-005: the room-level link into the US-only comparative page ───────────


def test_affordability_link_only_on_curated_rooms(tmp_path: Path) -> None:
    """A non-curated room never offers to compare itself across decades.

    ``affordability/index.html`` is projected over CURATED_COUNTRIES, so the
    link landed a UK or JP visitor on a page holding no fact of their country.
    """
    corpus = load_corpus(DATA)
    render_site(corpus, tmp_path, load_series(DATA), DATA)

    linked = {
        page.stem
        for page in (tmp_path / "rooms").glob("*.html")
        if PANEL_LINK in page.read_text()
    }
    assert linked, "no room links the affordability page — the gate is aimed wrong"

    countries = {slug.split("-", 1)[0] for slug in linked}
    assert countries <= curation.CURATED_COUNTRIES, (
        f"non-curated rooms link the US-only affordability page: "
        f"{sorted(countries - curation.CURATED_COUNTRIES)}"
    )

    # and the non-curated wings are genuinely present, or this proves nothing
    all_countries = {room.country for room in corpus.rooms}
    assert all_countries - curation.CURATED_COUNTRIES, (
        "every room is curated — this test cannot detect the bug it guards"
    )


def test_affordability_page_holds_only_curated_facts(tmp_path: Path) -> None:
    """The page the link points at really is single-country (the premise)."""
    corpus = load_corpus(DATA)
    render_site(corpus, tmp_path, load_series(DATA), DATA)

    page = (tmp_path / "affordability" / "index.html").read_text()
    foreign = sorted(
        room.country
        for room in corpus.rooms
        if room.country not in curation.CURATED_COUNTRIES
        and any(f.id in page for f in room.facts)
    )
    assert not foreign, f"the affordability page cites non-curated wings: {foreign}"


# ── FWI-004: the build-time gate over the decade-keyed registries ────────────


def test_committed_registries_pass_the_gate() -> None:
    validate_comparative_registries(load_corpus(DATA))


def _corpus_with_foreign_fact(corpus: Corpus, fact_id: str) -> Corpus:
    """Move ``fact_id`` into a fresh non-curated wing, keeping its decade."""
    donor = next(r for r in corpus.rooms if any(f.id == fact_id for f in r.facts))
    fact = next(f for f in donor.facts if f.id == fact_id)
    stripped = dataclasses.replace(
        donor, facts=tuple(f for f in donor.facts if f.id != fact_id)
    )
    foreign = Room(country="zz", decade=donor.decade, facts=(fact,))
    rooms = (*(stripped if r is donor else r for r in corpus.rooms), foreign)
    return dataclasses.replace(corpus, rooms=rooms)


def test_gate_rejects_a_registry_entry_from_a_non_curated_wing() -> None:
    """A curated registry naming another country's fact is a red build."""
    corpus = load_corpus(DATA)
    borrowed = curation.COMPOSITIONS["1970s"]
    with pytest.raises(ValueError) as excinfo:
        validate_comparative_registries(_corpus_with_foreign_fact(corpus, borrowed))
    message = str(excinfo.value)
    assert borrowed in message
    assert "'zz'" in message
    assert "COMPOSITIONS" in message


def test_gate_rejects_an_arc_entry_from_a_non_curated_wing() -> None:
    """The gate covers the arcs, not only the composition registry."""
    corpus = load_corpus(DATA)
    arc = next(a for a in curation.ARCS if a.fact_ids)
    borrowed = next(iter(arc.fact_ids.values()))
    with pytest.raises(ValueError) as excinfo:
        validate_comparative_registries(_corpus_with_foreign_fact(corpus, borrowed))
    assert f"ARCS[{arc.slug}]" in str(excinfo.value)


def test_gate_rejects_an_id_naming_no_room() -> None:
    """An unknown id is reported here rather than silently passing the gate."""
    corpus = load_corpus(DATA)
    compositions = set(curation.COMPOSITIONS.values())
    donor = next(r for r in corpus.rooms if any(f.id in compositions for f in r.facts))
    missing = next(f.id for f in donor.facts if f.id in compositions)
    stripped = dataclasses.replace(
        donor, facts=tuple(f for f in donor.facts if f.id != missing)
    )
    corpus = dataclasses.replace(
        corpus, rooms=tuple(stripped if r is donor else r for r in corpus.rooms)
    )
    with pytest.raises(ValueError, match="names no room's fact"):
        validate_comparative_registries(corpus)


# ── FWI-004: the affordability arc's decade key ──────────────────────────────


def test_afford_fact_ids_excludes_non_curated_rooms() -> None:
    """Every id the hours axis resolves belongs to a curated wing.

    Against the committed corpus this holds for a second reason — the arc
    patterns carry a ``us-`` prefix, so a UK room could not match one even
    unfiltered. That makes the assertion alone unable to detect the filter's
    removal, so the synthetic case below supplies a non-curated room whose
    fact id *does* match: without the filter it is resolved and the arc
    borrows it.
    """
    corpus = load_corpus(DATA)
    country_by_fact = {
        fact.id: room.country for room in corpus.rooms for fact in room.facts
    }
    resolved = [
        fid
        for _slug, _label, pattern in curation.AFFORD_ITEMS
        for fid in afford_fact_ids(corpus, pattern).values()
    ]
    assert resolved, "no affordability arc resolves — the gate is aimed wrong"
    assert {country_by_fact[fid] for fid in resolved} <= curation.CURATED_COUNTRIES

    # the load-bearing half: a non-curated wing holding a matching id
    synthetic = Corpus(
        sources={},
        assumptions={},
        rooms=(
            Room(country="zz", decade="1950s", facts=(_priced_fact("1950s-bread"),)),
        ),
    )
    assert afford_fact_ids(synthetic, "{decade}-bread") == {}


def _priced_fact(fact_id: str) -> Fact:
    return Fact(
        id=fact_id,
        panel=Panel.WORK_BUYS,
        label="a priced exhibit",
        value="1.00",
        unit="USD",
        source="s",
        tier=Tier.A,
    )


def test_afford_fact_ids_rejects_a_decade_collision() -> None:
    """Two curated rooms sharing a decade must redden, not overwrite.

    Today CURATED_COUNTRIES is US-only so the collision cannot occur; when a
    second country joins the story layer it will, and the last-wins dict would
    have put one country's price on the other's hours axis.
    """
    pattern = "{decade}-bread"
    rooms = (
        Room(country="us", decade="1950s", facts=(_priced_fact("1950s-bread"),)),
        Room(country="zz", decade="1950s", facts=(_priced_fact("1950s-bread"),)),
    )
    corpus = Corpus(sources={}, assumptions={}, rooms=rooms)

    # only "us" is curated: the second room is skipped, no collision
    assert afford_fact_ids(corpus, pattern) == {"1950s": "1950s-bread"}

    with pytest.raises(ValueError, match="share decade"), _curated({"us", "zz"}):
        afford_fact_ids(corpus, pattern)


class _curated:
    """Temporarily widen CURATED_COUNTRIES (it is read through the module)."""

    def __init__(self, countries: set[str]) -> None:
        self._countries = frozenset(countries)

    def __enter__(self) -> None:
        self._saved = curation.CURATED_COUNTRIES
        curation.CURATED_COUNTRIES = self._countries  # type: ignore[misc]

    def __exit__(self, *exc: object) -> None:
        curation.CURATED_COUNTRIES = self._saved  # type: ignore[misc]
