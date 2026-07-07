"""The gap inventory is mechanical: classified from the corpus, never hand-kept."""

from pathlib import Path

from vitrine.gaps import format_report, room_gaps
from vitrine.loader import load_corpus
from vitrine.model import Panel

DATA = Path(__file__).parent.parent / "data"


def _write_corpus(tmp_path: Path) -> Path:
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
        '[[fact]]\nid = "us-1950s-gap"\npanel = "home"\nlabel = "L"\n'
        'value = "no reliable record accessible online"\n'
        'unit = "n/a"\nsource = "src-1"\ntier = "D"\n\n'
        '[[fact]]\nid = "us-1950s-estimate"\npanel = "table"\nlabel = "L"\n'
        'value = "~$1,511"\nunit = "USD"\nsource = "src-1"\ntier = "D"\n\n'
        '[[fact]]\nid = "us-1950s-solid"\npanel = "budget"\nlabel = "L"\n'
        'value = "$3,319"\nunit = "USD"\nsource = "src-1"\ntier = "A"\n'
    )
    return tmp_path


def test_classification_is_mechanical(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus(tmp_path))
    (rg,) = room_gaps(corpus)

    assert rg.rendered_gaps == ("us-1950s-gap",)
    assert rg.tier_d_estimates == ("us-1950s-estimate",)
    # home, table, budget are populated; the other three panels are empty
    assert set(rg.empty_panels) == {Panel.DAY, Panel.DIFFUSION, Panel.WORK_BUYS}
    assert rg.n_facts == 3
    assert rg.n_tier_a == 1


def test_a_gap_value_is_never_double_counted_as_estimate(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus(tmp_path))
    (rg,) = room_gaps(corpus)
    assert "us-1950s-gap" not in rg.tier_d_estimates


def test_report_totals_line(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus(tmp_path))
    report = format_report(room_gaps(corpus))
    assert "us-1950s: 3 facts (1 Tier A)" in report
    assert "total: 3 facts across 1 rooms — 1 rendered gap(s), 1 Tier D estimate(s)" in report


def test_committed_corpus_inventory_runs(tmp_path: Path) -> None:
    rooms = room_gaps(load_corpus(DATA))
    assert len(rooms) >= 13
    report = format_report(rooms)
    assert report.splitlines()[-1].startswith("total:")
