"""Compact structural contracts for the presentation layer.

Two layers:

1. **Exact snapshot** (``test_page_contract``): pins the shape most likely to
   change during template work — page landmarks, disclosure counts, local
   destinations, provenance overlays, and the set of fact marks — for 11
   representative pages. Text and SVG bytes intentionally remain free to
   improve. These are characterization snapshots, not visual snapshots; update
   the inline literals when a page changes intentionally.

2. **Stable invariants**: discovers *every* rendered page from the built output
   and asserts properties that should never change regardless of data or
   template evolution — landmarks, nav, unique titles, modal-target
   resolution, source-card disclosures, panel sections, and the composite-
   family disclaimer. These catch regressions to the site's skeleton across all
   ~114 pages (including UK/JP rooms and corridor pairs) without the maintenance
   burden of exact-count pinning.

Re-baselined for Plan 020 (the statistical atlas redesign): the fact-mark
hashes, overlay counts, and every pair/walkthrough/affordability structure
survived the redesign untouched; what changed is deliberate — index gained
the corpus-matrix links, room panels became sections (each carrying one
in-page record drawer per fact), and a colophon footer joined every page.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site.render import render_site

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("contract-site")
    render_site(load_corpus(DATA), out, load_series(DATA), DATA)
    return out


@dataclass(frozen=True, slots=True)
class PageContract:
    title: str
    header: int
    nav: int
    main: int
    section: int
    footer: int
    details: int
    details_open: int
    local_links: int
    local_links_hash: str
    fact_marks: int
    fact_marks_hash: str
    placard_overlays: int


class _ContractScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_done = False
        self.title_parts: list[str] = []
        self.tags: dict[str, int] = {}
        self.details = 0
        self.details_open = 0
        self.local_hrefs: set[str] = set()
        self.fact_marks: set[str] = set()
        self.placard_overlays = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attr = dict(attrs)
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if tag == "title" and not self.title_done:
            self.in_title = True
        if tag == "details":
            self.details += 1
            if "open" in attr:
                self.details_open += 1
        href = attr.get("href")
        if href and not href.startswith(("http://", "https://", "mailto:")):
            self.local_hrefs.add(href)
        fact_id = attr.get("data-fact-id")
        if fact_id:
            self.fact_marks.add(fact_id)
        element_id = attr.get("id")
        if element_id and element_id.endswith("--modal"):
            self.placard_overlays += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.in_title:
            self.in_title = False
            self.title_done = True

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def _digest(values: set[str]) -> str:
    payload = "\n".join(sorted(values)).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def _contract(page: Path) -> PageContract:
    scanner = _ContractScanner()
    scanner.feed(page.read_text())
    return PageContract(
        title="".join(scanner.title_parts).strip(),
        header=scanner.tags.get("header", 0),
        nav=scanner.tags.get("nav", 0),
        main=scanner.tags.get("main", 0),
        section=scanner.tags.get("section", 0),
        footer=scanner.tags.get("footer", 0),
        details=scanner.details,
        details_open=scanner.details_open,
        local_links=len(scanner.local_hrefs),
        local_links_hash=_digest(scanner.local_hrefs),
        fact_marks=len(scanner.fact_marks),
        fact_marks_hash=_digest(scanner.fact_marks),
        placard_overlays=scanner.placard_overlays,
    )


# Values are deliberately explicit. When a page changes intentionally, inspect
# the structural diff before updating its one compact row.
def _page(
    title: str,
    *,
    landmarks: tuple[int, int, int, int, int],
    disclosures: tuple[int, int],
    local: tuple[int, str],
    marks: tuple[int, str],
    overlays: int,
) -> PageContract:
    return PageContract(
        title,
        *landmarks,
        *disclosures,
        *local,
        *marks,
        overlays,
    )


EXPECTED: dict[str, PageContract] = {
    "index.html": _page(
        "vitrine — the median family's century",
        landmarks=(1, 2, 1, 0, 1), disclosures=(0, 0),
        local=(104, "7f0ea353b6ce"), marks=(0, "e3b0c44298fc"), overlays=0,
    ),
    "rooms/us-1950s.html": _page(
        "US · 1950s — vitrine",
        landmarks=(1, 3, 1, 7, 1), disclosures=(85, 0),
        local=(82, "367342b2b071"), marks=(10, "1ef9c695b820"), overlays=41,
    ),
    "rooms/us-1910s.html": _page(
        "US · 1910s — vitrine",
        landmarks=(1, 3, 1, 7, 1), disclosures=(30, 0),
        local=(48, "68e378f315fd"), marks=(6, "f83300610bb2"), overlays=15,
    ),
    "corridors/index.html": _page(
        "corridors — vitrine",
        landmarks=(5, 2, 1, 5, 1), disclosures=(281, 4),
        local=(348, "c2ff69ead178"), marks=(249, "7992409d6a16"), overlays=249,
    ),
    "corridors/1900s--2020s.html": _page(
        "1900s ↔ 2020s — vitrine corridors",
        landmarks=(1, 1, 1, 0, 1), disclosures=(22, 0),
        local=(38, "115ac2e25f0e"), marks=(21, "85b5b512d0b6"), overlays=21,
    ),
    "affordability/index.html": _page(
        "affordability — vitrine",
        landmarks=(1, 1, 1, 0, 2), disclosures=(0, 0),
        local=(18, "bb96ecf96a67"), marks=(9, "cc00d43721f7"), overlays=0,
    ),
    "walkthrough.html": _page(
        "the walkthrough — vitrine",
        landmarks=(1, 1, 1, 0, 1), disclosures=(53, 0),
        local=(75, "76746a47d2a1"), marks=(53, "6de4963985b6"), overlays=53,
    ),
    "methodology.html": _page(
        "methodology — vitrine",
        landmarks=(1, 1, 1, 0, 1), disclosures=(0, 0),
        local=(9, "9f9775dbe453"), marks=(0, "e3b0c44298fc"), overlays=0,
    ),
    "bibliography.html": _page(
        "bibliography — vitrine",
        landmarks=(1, 1, 1, 0, 1), disclosures=(95, 0),
        local=(9, "9f9775dbe453"), marks=(0, "e3b0c44298fc"), overlays=0,
    ),
    "essays/index.html": _page(
        "docent tours — vitrine",
        landmarks=(1, 1, 1, 0, 1), disclosures=(34, 0),
        local=(17, "5d4fffb77a0e"), marks=(0, "e3b0c44298fc"), overlays=34,
    ),
    "essays/one-paycheck.html": _page(
        "One paycheck — docent tours · vitrine",
        landmarks=(1, 1, 1, 0, 1), disclosures=(7, 0),
        local=(27, "9b2e9f014989"), marks=(9, "d7a0f3435114"), overlays=7,
    ),
}


@pytest.mark.parametrize("relative", tuple(EXPECTED))
def test_page_contract(site: Path, relative: str) -> None:
    actual = _contract(site / relative)
    assert asdict(actual) == asdict(EXPECTED[relative])


# ── Stable structural invariants (all rendered pages) ──────────────────────
#
# These check properties that should *never* change regardless of data or
# template evolution — page landmarks that define the site's structure, the
# composite-family disclaimer, the footer, etc. Unlike the exact-contract test
# above (which pins counts and hashes for 11 pages and changes on every data
# update), these invariants are discovered from the built output and cover
# every rendered page — currently ~114 pages including all UK/JP rooms and
# corridor pairs.


@pytest.fixture(scope="module")
def all_pages(site: Path) -> list[str]:
    """Every rendered HTML page, as a relative posix path."""
    return sorted(p.relative_to(site).as_posix() for p in site.rglob("*.html"))


@pytest.fixture(scope="module")
def all_room_pages(all_pages: list[str]) -> list[str]:
    return [p for p in all_pages if p.startswith("rooms/")]


def test_page_titles_are_unique(site: Path, all_pages: list[str]) -> None:
    """No two pages should share the same title — duplicates indicate a broken
    {% block title %} override."""
    titles: dict[str, str] = {}
    for relative in all_pages:
        actual = _contract(site / relative)
        assert actual.title, f"{relative} has no title"
        if actual.title in titles:
            raise AssertionError(
                f"Duplicate title {actual.title!r} on {relative} and {titles[actual.title]}"
            )
        titles[actual.title] = relative


def test_page_has_landmarks(site: Path, all_pages: list[str]) -> None:
    """Every page must have at least one <header>, exactly one <main>, and at
    least one <footer>."""
    for relative in all_pages:
        actual = _contract(site / relative)
        assert actual.header >= 1, f"{relative}: expected >=1 header, got {actual.header}"
        assert actual.main == 1, f"{relative}: expected 1 main, got {actual.main}"
        assert actual.footer >= 1, f"{relative}: expected >=1 footer, got {actual.footer}"


def test_page_has_nav(site: Path, all_pages: list[str]) -> None:
    """Every page must have at least one <nav> element."""
    for relative in all_pages:
        actual = _contract(site / relative)
        assert actual.nav >= 1, f"{relative}: expected >=1 nav, got {actual.nav}"


def test_modal_targets_resolve(site: Path, all_pages: list[str]) -> None:
    """Every local href of the form '#<id>--modal' must resolve to an element
    with that id on the same page. Catches broken placard-overlay links."""
    for relative in all_pages:
        html = (site / relative).read_text()
        scanner = _ContractScanner()
        scanner.feed(html)
        for href in scanner.local_hrefs:
            if href.startswith("#") and href.endswith("--modal"):
                target_id = href[1:]  # strip leading #
                assert f'id="{target_id}"' in html, (
                    f"{relative}: href '{href}' targets #{target_id} which does not exist"
                )


def test_room_pages_have_disclosures(site: Path, all_room_pages: list[str]) -> None:
    """Every room page must have at least two <details> elements (source-card
    drawers). >=2 is a coarse canary: the authoritative per-fact guarantee is
    the render-coverage gate in check.py; this catches total structural loss."""
    for relative in all_room_pages:
        actual = _contract(site / relative)
        assert actual.details >= 2, (
            f"{relative}: room page has only {actual.details} details elements"
        )


def test_room_pages_have_sections(site: Path, all_room_pages: list[str]) -> None:
    """Every room page must have multiple <section> elements (one per panel).
    A room with zero or one sections has lost its panel structure."""
    for relative in all_room_pages:
        actual = _contract(site / relative)
        assert actual.section >= 2, f"{relative}: expected >=2 sections, got {actual.section}"


def test_room_pages_have_composite_family_disclaimer(
    site: Path, all_room_pages: list[str]
) -> None:
    """Every room page must render the composite-family disclaimer in a
    structural element. Removing or hiding it is a charter violation
    (AGENTS.md: hard rules). This checks for the .room-disclaimer element with
    non-empty text content, not a copy-coupled substring."""
    from vitrine.loader import load_corpus

    corpus = load_corpus(DATA)
    expected_statement = corpus.assumptions.get("composite-family")
    for relative in all_room_pages:
        html = (site / relative).read_text()
        # Structural check: the room-disclaimer element must be present.
        assert 'class="plaque room-disclaimer"' in html, (
            f"{relative}: composite-family disclaimer element not found"
        )
        # Data-driven check: the curated statement text must appear (proves the
        # actual disclaimer shipped, not just an empty div).
        if expected_statement:
            # Use the first sentence of the statement as the marker — robust to
            # minor wording changes in the rest of the statement.
            first_sentence = expected_statement.statement.split(".")[0]
            assert first_sentence.strip() in html, (
                f"{relative}: disclaimer statement text not found"
            )
