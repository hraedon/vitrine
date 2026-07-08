"""Plan 007 acceptance criteria over the built site.

Builds once per session from the committed corpus and asserts on the actual
HTML: static (no script), marks resolve, symbols gated per room, deep links
land, gaps render as gaps.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

from vitrine.check import check_mark_coverage
from vitrine.loader import load_corpus
from vitrine.model import Corpus
from vitrine.site import curation, symbols
from vitrine.site.render import render_site

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def corpus() -> Corpus:
    return load_corpus(DATA)


@pytest.fixture(scope="module")
def site(corpus: Corpus, tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("site")
    render_site(corpus, out)
    return out


class _Scanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.mark_ids: list[str] = []
        self.hrefs: list[str] = []
        self.anchor_ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        for name, value in attrs:
            if name == "data-fact-id" and value:
                self.mark_ids.append(value)
            if name == "href" and value:
                self.hrefs.append(value)
            if name == "id" and value:
                self.anchor_ids.add(value)


def _scan(page: Path) -> _Scanner:
    scanner = _Scanner()
    scanner.feed(page.read_text())
    return scanner


def test_no_script_anywhere(site: Path) -> None:
    """AC 1: all static — no <script> in any truth-path page."""
    for page in site.rglob("*.html"):
        assert "script" not in _scan(page).tags, f"<script> in {page.name}"


def test_all_three_surfaces_render(site: Path, corpus: Corpus) -> None:
    """AC 1/5: rooms, corridors, and the walkthrough all exist."""
    assert (site / "walkthrough.html").is_file()
    assert (site / "corridors" / "index.html").is_file()
    n = len(corpus.rooms)
    assert len(list((site / "rooms").glob("*.html"))) == n
    assert len(list((site / "corridors").glob("*--*.html"))) == n * (n - 1) // 2


def test_mark_coverage_green_on_build(site: Path, corpus: Corpus) -> None:
    assert check_mark_coverage(corpus, site) == []


def test_mark_coverage_red_on_unresolvable_mark(site: Path, corpus: Corpus, tmp_path: Path) -> None:
    """AC 2: a mark that names a fact the corpus doesn't have is a red build."""
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "page.html").write_text('<div data-fact-id="us-1950s-ghost">x</div>')
    problems = check_mark_coverage(corpus, bad)
    assert any("us-1950s-ghost" in p for p in problems)


def test_room_marks_stay_in_room(site: Path) -> None:
    """AC 4 (and honesty): every mark on a room page projects that room's facts —
    a symbol can't borrow another decade's diffusion fact."""
    for page in (site / "rooms").glob("*.html"):
        prefix = page.stem + "-"  # us-1950s-
        for mark_id in _scan(page).mark_ids:
            assert mark_id.startswith(prefix), f"{page.name}: foreign mark {mark_id}"


def test_absent_technology_is_not_drawn(site: Path, corpus: Corpus) -> None:
    """AC 4: a stage artifact appears only when its registry fact exists in the room."""
    for room in corpus.rooms:
        page = site / "rooms" / f"{room.slug}.html"
        room_ids = {f.id for f in room.facts}
        html = page.read_text()
        for artifact in ("television", "internet", "air-conditioning", "cable", "computer"):
            fid = curation.STAGE_DIFFUSION.get(artifact, {}).get(room.decade)
            sym = symbols.symbol(artifact, room.decade)
            assert sym is not None
            drawn = sym.svg[:60] in html
            if fid is None:
                assert not drawn, f"{room.slug}: {artifact} drawn without a fact"
            else:
                assert fid in room_ids
                assert drawn, f"{room.slug}: {artifact} has a fact but wasn't drawn"


def test_era_keyed_symbols() -> None:
    """The icebox precedes the round-top precedes the two-door."""
    assert symbols.symbol("refrigerator", "1900s").variant == "icebox"  # type: ignore[union-attr]
    assert symbols.symbol("refrigerator", "1950s").variant == "round-top"  # type: ignore[union-attr]
    assert symbols.symbol("refrigerator", "2020s").variant == "two-door"  # type: ignore[union-attr]
    assert symbols.symbol("telephone", "1900s").variant == "candlestick"  # type: ignore[union-attr]
    assert symbols.symbol("telephone", "2020s").variant == "smartphone"  # type: ignore[union-attr]
    assert symbols.symbol("no-such-artifact", "1950s") is None


def test_chart_deep_links_resolve(site: Path) -> None:
    """WI-6 / Plan 009: every corridor mark links to a resolvable placard.

    Click targets are now in-page overlays (``#fact-id--modal``); the deep link
    to the room placard is preserved as the fallback path when a path is given.
    """
    for page in [site / "corridors" / "index.html", site / "walkthrough.html"]:
        base = page.parent
        for href in _scan(page).hrefs:
            if "#" not in href or href.startswith("http") or href == "#":
                continue
            path, _, anchor = href.partition("#")
            if not path:
                # in-page CSS-only overlay anchor; must exist on the same page
                assert anchor in _scan(page).anchor_ids, f"{page.name}: dead overlay anchor {href}"
                continue
            target = (base / path).resolve()
            assert target.is_file(), f"{page.name}: dead link {href}"
            assert anchor in _scan(target).anchor_ids, f"{page.name}: dead anchor {href}"


def test_gaps_render_as_gaps_not_numbers(site: Path, corpus: Corpus) -> None:
    """A fact without a structured quantity never becomes chart geometry."""
    corridor = (site / "corridors" / "index.html").read_text()
    # the 1990s Ramey gap: its mark exists (a gap slot), but never as a dot with a value
    assert 'data-fact-id="us-1990s-home-production-women"' in corridor
    gap_mark = re.search(
        r'<g data-fact-id="us-1990s-home-production-women">.*?</g>', corridor, re.S
    )
    assert gap_mark is not None
    assert 'class="gapdot"' in gap_mark.group(0)
    assert 'class="dot"' not in gap_mark.group(0)


def test_walkthrough_meter_and_house_are_honest(site: Path) -> None:
    """The 2020s meter row is the concept-splice gap; only sourced floor area scales."""
    html = (site / "walkthrough.html").read_text()
    assert "concept splice" in html
    assert "1,500 sq ft (sourced)" in html
    assert "floor area not yet curated" in html


def test_era_graded_light_varies(site: Path) -> None:
    """The stage glow tint differs between the 1900s and 2020s rooms."""
    page_1900s = (site / "rooms" / "us-1900s.html").read_text()
    page_2020s = (site / "rooms" / "us-2020s.html").read_text()
    from vitrine.site import tokens

    assert tokens.ERA_GLOW["1900s"] in page_1900s
    assert tokens.ERA_GLOW["2020s"] in page_2020s
    assert tokens.ERA_GLOW["2020s"] not in page_1900s
