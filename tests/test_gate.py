"""The provenance gate: green on the committed corpus, red on broken data."""

from pathlib import Path

import pytest

from vitrine.check import check_corpus
from vitrine.loader import LoadError, load_corpus

DATA = Path(__file__).parent.parent / "data"


def test_committed_corpus_is_green() -> None:
    corpus = load_corpus(DATA)
    assert check_corpus(corpus) == []
    assert corpus.rooms, "corpus must contain at least one room"


def _write_minimal(tmp_path: Path, fact_source: str = "src-1") -> Path:
    (tmp_path / "sources.toml").write_text(
        '[[source]]\nid = "src-1"\ntitle = "T"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "all families"\n'
    )
    (tmp_path / "assumptions.toml").write_text(
        '[[assumption]]\nid = "composite-family"\ntitle = "A"\nstatement = "S"\n'
    )
    room_dir = tmp_path / "us"
    room_dir.mkdir()
    (room_dir / "1950s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n'
        '[[fact]]\nid = "us-1950s-x"\npanel = "budget"\nlabel = "L"\nvalue = "V"\n'
        f'unit = "U"\nsource = "{fact_source}"\ntier = "A"\n'
    )
    return tmp_path


def test_dangling_source_fails_gate(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path, fact_source="no-such-source")
    problems = check_corpus(load_corpus(data))
    assert any("unknown source" in p for p in problems)


def test_valid_minimal_corpus_passes(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    assert check_corpus(load_corpus(data)) == []


def test_bad_tier_rejected_at_parse(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    room = data / "us" / "1950s.toml"
    room.write_text(room.read_text().replace('tier = "A"', 'tier = "Z"'))
    with pytest.raises(LoadError, match="tier 'Z'"):
        load_corpus(data)


def test_wrong_id_prefix_fails_gate(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    room = data / "us" / "1950s.toml"
    room.write_text(room.read_text().replace('id = "us-1950s-x"', 'id = "uk-1950s-x"'))
    problems = check_corpus(load_corpus(data))
    assert any("must start with" in p for p in problems)
