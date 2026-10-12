"""The two curation layers — enrollment vs comparative membership (plan 031).

Enrolling a country (authoring its room stories, adding it to
CURATED_COUNTRIES) must be buildable *without* that country joining the
decade-keyed comparative analyses (COMPARATIVE_COUNTRIES): before plan 031
the walkthrough's decade guard went red on a second curated "1950s" and the
pair loop double-wrote its pages. These tests simulate the UK's enrollment
by widening CURATED_COUNTRIES alone — the same world the story layer will
create for real — and pin what must and must not change.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation
from vitrine.site.render import render_site

DATA = Path(__file__).parent.parent / "data"

PANEL_LINK = "See this metric across all decades"


class _enrolled:
    """Temporarily widen CURATED_COUNTRIES, leaving COMPARATIVE_COUNTRIES
    alone — an enrolled-but-not-comparative wing (read through the module)."""

    def __init__(self, countries: set[str]) -> None:
        self._countries = frozenset(countries)

    def __enter__(self) -> None:
        self._saved = curation.CURATED_COUNTRIES
        curation.CURATED_COUNTRIES = self._countries  # type: ignore[misc]

    def __exit__(self, *exc: object) -> None:
        curation.CURATED_COUNTRIES = self._saved  # type: ignore[misc]


def test_simulated_uk_enrollment_builds_and_holds_the_layers(tmp_path: Path) -> None:
    corpus = load_corpus(DATA)
    us = [r for r in corpus.rooms if r.country == "us"]
    uk = [r for r in corpus.rooms if r.country == "uk"]
    assert uk, "the committed corpus has no UK wing — this test simulates nothing"

    with _enrolled({"us", "uk"}):
        render_site(corpus, tmp_path, load_series(DATA), DATA)

        # the comparative layer stays the US analyses: the walkthrough
        # builds (no decade collision) and the pairwise set is US-only
        assert (tmp_path / "walkthrough.html").is_file()
        pairs = list((tmp_path / "corridors").glob("*--*.html"))
        assert len(pairs) == len(us) * (len(us) - 1) // 2

        # enrolled rooms join the lobby matrix, labelled by country
        lobby = (tmp_path / "index.html").read_text()
        assert lobby.count("<tr>") >= len(us) + len(uk)
        assert 'href="rooms/uk-1970s.html"' in lobby
        assert ">UK 1970s</a>" in lobby
        assert ">1970s</a>" in lobby  # the US row keeps its bare label

        # the room-level comparative link is gated on the comparative layer,
        # not enrollment: US rooms link it, enrolled UK rooms do not (FWI-005)
        linked = {
            page.stem
            for page in (tmp_path / "rooms").glob("*.html")
            if PANEL_LINK in page.read_text()
        }
        assert linked == {room.slug for room in us}

        # every room still renders
        assert len(list((tmp_path / "rooms").glob("*.html"))) == len(corpus.rooms)


def test_comparative_countries_must_stay_inside_the_curated_set(
    tmp_path: Path,
) -> None:
    """A country cannot be comparative without being enrolled."""
    corpus = load_corpus(DATA)
    with _enrolled(set()), pytest.raises(ValueError, match="comparative but not curated"):
        render_site(corpus, tmp_path, load_series(DATA), DATA)
