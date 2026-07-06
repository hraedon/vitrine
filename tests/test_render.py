"""V0 renderer: builds from the committed corpus, disclaimer on every room."""

from pathlib import Path

from vitrine.loader import load_corpus
from vitrine.site.render import render_site

DATA = Path(__file__).parent.parent / "data"


def test_render_committed_corpus(tmp_path: Path) -> None:
    corpus = load_corpus(DATA)
    render_site(corpus, tmp_path)

    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "methodology.html").is_file()

    room_pages = list((tmp_path / "rooms").glob("*.html"))
    assert len(room_pages) == len(corpus.rooms)
    disclaimer_fragment = "statistical composite"
    for page in room_pages:
        assert disclaimer_fragment in page.read_text(), f"disclaimer missing from {page.name}"

    manifest = (tmp_path / "facts-manifest.txt").read_text().split()
    curated = sorted(f.id for room in corpus.rooms for f in room.facts)
    assert sorted(manifest) == curated
