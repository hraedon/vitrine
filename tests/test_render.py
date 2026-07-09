"""V0 renderer: builds from the committed corpus, disclaimer on every room."""

from pathlib import Path

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site.render import render_site

DATA = Path(__file__).parent.parent / "data"


def test_render_committed_corpus(tmp_path: Path) -> None:
    corpus = load_corpus(DATA)
    render_site(corpus, tmp_path, load_series(DATA), DATA)

    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "methodology.html").is_file()

    room_pages = list((tmp_path / "rooms").glob("*.html"))
    assert len(room_pages) == len(corpus.rooms)
    disclaimer_fragment = "statistical composite"
    for page in room_pages:
        assert disclaimer_fragment in page.read_text(), f"disclaimer missing from {page.name}"

    manifest = (tmp_path / "facts-manifest.txt").read_text().split()
    curated = sorted(
        [f.id for room in corpus.rooms for f in room.facts]
        + [d.id for room in corpus.rooms for d in room.derived]
    )
    assert sorted(manifest) == curated


def test_derived_facts_render_computed_values(tmp_path: Path) -> None:
    """Plan 006: the displayed value of a derived fact is computed, not authored."""
    corpus = load_corpus(DATA)
    render_site(corpus, tmp_path, load_series(DATA), DATA)

    page_1950s = (tmp_path / "rooms" / "us-1950s.html").read_text()
    # 735400 / 367500 minor units — computed at build, tier = weakest input (C)
    assert "≈ 2.0" in page_1950s
    assert "Computed by vitrine" in page_1950s

    page_2020s = (tmp_path / "rooms" / "us-2020s.html").read_text()
    # 36060000 / 13990000 minor units, precision 2, both inputs Tier A
    assert "≈ 2.58" in page_2020s
