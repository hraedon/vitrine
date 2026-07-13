"""Compact structural contracts for Plan 018's presentation refactor.

These are characterization snapshots, not visual snapshots. They pin the
shape most likely to disappear during template extraction: page landmarks,
native disclosure state, local destinations, provenance overlays, and the set
of fact marks. Text and SVG bytes intentionally remain free to improve.
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
        "vitrine — the museum lobby",
        landmarks=(1, 2, 1, 0, 0), disclosures=(0, 0),
        local=(21, "2911f436424d"), marks=(0, "e3b0c44298fc"), overlays=0,
    ),
    "rooms/us-1950s.html": _page(
        "US · 1950s — vitrine",
        landmarks=(1, 3, 1, 1, 0), disclosures=(89, 6),
        local=(48, "c8cdfe41eccc"), marks=(10, "1ef9c695b820"), overlays=40,
    ),
    "rooms/us-1910s.html": _page(
        "US · 1910s — vitrine",
        landmarks=(1, 3, 1, 1, 0), disclosures=(34, 6),
        local=(37, "360a2bd931a7"), marks=(6, "f83300610bb2"), overlays=14,
    ),
    "corridors/index.html": _page(
        "corridors — vitrine",
        landmarks=(5, 2, 1, 5, 0), disclosures=(281, 4),
        local=(347, "b0498ecb7765"), marks=(249, "7992409d6a16"), overlays=249,
    ),
    "corridors/1900s--2020s.html": _page(
        "1900s ↔ 2020s — vitrine corridors",
        landmarks=(1, 1, 1, 0, 0), disclosures=(22, 0),
        local=(37, "f1c5eabd2f3c"), marks=(21, "85b5b512d0b6"), overlays=21,
    ),
    "affordability/index.html": _page(
        "affordability — vitrine",
        landmarks=(1, 1, 1, 0, 1), disclosures=(0, 0),
        local=(17, "55b9a8ae5d8b"), marks=(9, "cc00d43721f7"), overlays=0,
    ),
    "walkthrough.html": _page(
        "the walkthrough — vitrine",
        landmarks=(1, 1, 1, 0, 0), disclosures=(53, 0),
        local=(74, "81673a9f58f7"), marks=(53, "6de4963985b6"), overlays=53,
    ),
    "methodology.html": _page(
        "methodology — vitrine",
        landmarks=(1, 1, 1, 0, 0), disclosures=(0, 0),
        local=(8, "7329590bb4c4"), marks=(0, "e3b0c44298fc"), overlays=0,
    ),
    "bibliography.html": _page(
        "bibliography — vitrine",
        landmarks=(1, 1, 1, 0, 0), disclosures=(80, 0),
        local=(8, "7329590bb4c4"), marks=(0, "e3b0c44298fc"), overlays=0,
    ),
}


@pytest.mark.parametrize("relative", tuple(EXPECTED))
def test_page_contract(site: Path, relative: str) -> None:
    actual = _contract(site / relative)
    assert asdict(actual) == asdict(EXPECTED[relative])
