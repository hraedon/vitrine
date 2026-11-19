"""A renderer's manifest cannot vouch for rows missing from its HTML."""

from pathlib import Path

import pytest

from vitrine.check import check_render_coverage
from vitrine.loader import load_corpus
from vitrine.model import Corpus
from vitrine.series import load_series
from vitrine.site.build import build_site

DATA = Path(__file__).parent.parent / "data"


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> tuple[Corpus, Path]:
    corpus = load_corpus(DATA)
    out = tmp_path_factory.mktemp("coverage-site")
    build_site(corpus, out, load_series(DATA), DATA)
    assert check_render_coverage(corpus, out) == []
    return corpus, out


@pytest.mark.parametrize("kind", ["observation", "gap", "calculation"])
def test_missing_row_fails_even_with_manifest_and_modal(
    built: tuple[Corpus, Path], kind: str,
) -> None:
    corpus, out = built
    room = next(room for room in corpus.rooms if room.derived and any(
        fact.value.startswith("no reliable record") for fact in room.facts
    ))
    if kind == "calculation":
        record_id = room.derived[0].id
    else:
        record_id = next(fact.id for fact in room.facts if (
            fact.value.startswith("no reliable record") == (kind == "gap")
        ))
    page = out / "rooms" / f"{room.slug}.html"
    original = page.read_text(encoding="utf-8")
    try:
        # Leave its overlay and the manifest intact; remove only the row id.
        page.write_text(original.replace(f'id="{record_id}"', 'id="omitted"'), encoding="utf-8")
        assert any(record_id in p and "missing record row" in p
                   for p in check_render_coverage(corpus, out))
    finally:
        page.write_text(original, encoding="utf-8")


@pytest.mark.parametrize("failure", ["missing-page", "borrowed", "duplicate"])
def test_room_membership_and_unique_rows(
    built: tuple[Corpus, Path], failure: str,
) -> None:
    corpus, out = built
    room = corpus.rooms[0]
    page = out / "rooms" / f"{room.slug}.html"
    original = page.read_text(encoding="utf-8")
    try:
        if failure == "missing-page":
            page.unlink()
            expected = "not found"
        else:
            record_id = room.facts[0].id if failure == "duplicate" else corpus.rooms[1].facts[0].id
            page.write_text(original + f'<div class="fact-row" id="{record_id}"></div>',
                            encoding="utf-8")
            expected = "duplicate record row" if failure == "duplicate" else "unexpected record row"
        assert any(expected in p for p in check_render_coverage(corpus, out))
    finally:
        page.write_text(original, encoding="utf-8")
