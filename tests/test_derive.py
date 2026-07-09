"""Derived facts: structure is authored, numbers are computed (plan 006)."""

from pathlib import Path

import pytest

from vitrine.check import check_corpus
from vitrine.derive import DeriveError, evaluate, evaluate_room
from vitrine.loader import load_corpus
from vitrine.model import (
    DerivedFact,
    DerivedOp,
    Fact,
    Panel,
    Room,
    Tier,
)

DATA = Path(__file__).parent.parent / "data"


def _fact(fact_id: str, amount: int | None, tier: Tier = Tier.A, currency: str = "USD") -> Fact:
    return Fact(
        id=fact_id,
        panel=Panel.BUDGET,
        label="L",
        value="V",
        unit="U",
        source="src-1",
        tier=tier,
        amount_minor=amount,
        currency=currency if amount is not None else "",
        price_year=1950 if amount is not None else None,
        basis=None,
    )


def _derived(op: DerivedOp = DerivedOp.RATIO, precision: int = 1) -> DerivedFact:
    return DerivedFact(
        id="us-1950s-d",
        panel=Panel.WORK_BUYS,
        label="D",
        unit="years",
        op=op,
        numerator="us-1950s-a",
        denominator="us-1950s-b",
        precision=precision,
    )


def _room(facts: tuple[Fact, ...], derived: tuple[DerivedFact, ...] = ()) -> Room:
    return Room(country="us", decade="1950s", facts=facts, derived=derived)


def test_ratio_value_and_weakest_tier() -> None:
    room = _room((_fact("us-1950s-a", 735400, Tier.C), _fact("us-1950s-b", 367500, Tier.A)))
    computed = evaluate(room, _derived())
    assert computed.value == "≈ 2.0"
    assert computed.tier is Tier.C  # weakest input wins, mechanically


def test_pct_of_value() -> None:
    room = _room((_fact("us-1950s-a", 5329), _fact("us-1950s-b", 331900)))
    computed = evaluate(room, _derived(op=DerivedOp.PCT_OF))
    assert computed.value == "≈ 1.6%"


def test_zero_denominator_raises() -> None:
    room = _room((_fact("us-1950s-a", 100), _fact("us-1950s-b", 0)), (_derived(),))
    with pytest.raises(DeriveError, match=r"denominator .* is zero"):
        evaluate_room(room)


def test_currency_mismatch_raises() -> None:
    room = _room(
        (_fact("us-1950s-a", 100), _fact("us-1950s-b", 100, currency="GBP")), (_derived(),)
    )
    with pytest.raises(DeriveError, match="currency mismatch"):
        evaluate_room(room)


def test_unstructured_operand_raises() -> None:
    room = _room((_fact("us-1950s-a", 100), _fact("us-1950s-b", None)), (_derived(),))
    with pytest.raises(DeriveError, match="no amount_minor"):
        evaluate_room(room)


# ── The gate catches broken derived structure before render ─────────────────


def _write_corpus_with_derived(tmp_path: Path, denominator: str) -> Path:
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
        '[[fact]]\nid = "us-1950s-a"\npanel = "budget"\nlabel = "L"\nvalue = "V"\n'
        'unit = "U"\nsource = "src-1"\ntier = "A"\namount_minor = 100\n'
        'currency = "USD"\nprice_year = 1950\nbasis = "annual"\n\n'
        '[[derived]]\nid = "us-1950s-d"\npanel = "work-buys"\nlabel = "D"\n'
        'unit = "years"\nop = "ratio"\nnumerator = "us-1950s-a"\n'
        f'denominator = "{denominator}"\n'
    )
    return tmp_path


def test_gate_flags_dangling_operand(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_derived(tmp_path, "us-1950s-nope"))
    problems = check_corpus(corpus)
    assert any("us-1950s-d" in p and "does not resolve" in p for p in problems)


def test_gate_green_on_valid_derived(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_derived(tmp_path, "us-1950s-a"))
    assert check_corpus(corpus) == []


def test_committed_corpus_derived_all_evaluate() -> None:
    from vitrine.series import load_series

    corpus = load_corpus(DATA)
    series = load_series(DATA)
    n = 0
    for room in corpus.rooms:
        n += len(evaluate_room(room, series))
    assert n >= 3  # two home-as-income-years + one car-price inflate (Plan 012)


# ── INFLATE op (Plan 012 WI-1) ───────────────────────────────────────────────


def _inflate_derived(
    series_id: str = "cpi-test", from_yr: int = 2020, to_yr: int = 2024
) -> DerivedFact:
    return DerivedFact(
        id="us-2020s-d",
        panel=Panel.WORK_BUYS,
        label="D",
        unit="USD",
        op=DerivedOp.INFLATE,
        numerator="us-2020s-base",
        denominator="",
        precision=0,
        inflate_series=series_id,
        inflate_from_year=from_yr,
        inflate_to_year=to_yr,
    )


def _inflate_series(values: dict[int, float]) -> dict:
    from vitrine.series import Series
    return {"cpi-test": Series(
        id="cpi-test", label="L", source="src-1", tier=Tier.A,
        unit="index", population="p", values=values,
    )}


def test_inflate_computes_correct_value() -> None:
    """$27,366 (cents: 2736600) x 177.886/147.600 = ~$32,981."""
    room = _room((_fact("us-2020s-base", 2736600, Tier.A),))
    series = _inflate_series({2020: 147.600, 2024: 177.886})
    computed = evaluate(room, _inflate_derived(), series)
    assert computed.value == "≈ $32,981"
    assert computed.tier is Tier.A  # both inputs Tier A


def test_inflate_tier_is_weakest_input() -> None:
    """A Tier C inflation series weakens the derived tier."""
    from vitrine.series import Series
    room = _room((_fact("us-2020s-base", 2736600, Tier.A),))
    series = {"cpi-test": Series(
        id="cpi-test", label="L", source="src-1", tier=Tier.C,
        unit="index", population="p", values={2020: 100.0, 2024: 120.0},
    )}
    computed = evaluate(room, _inflate_derived(), series)
    assert computed.tier is Tier.C  # weakest input — series is C


def test_inflate_missing_series_raises() -> None:
    room = _room((_fact("us-2020s-base", 2736600),))
    with pytest.raises(DeriveError, match="not available"):
        evaluate(room, _inflate_derived(), {})


def test_inflate_missing_year_raises() -> None:
    room = _room((_fact("us-2020s-base", 2736600),))
    series = _inflate_series({2020: 147.6})  # no 2024
    with pytest.raises(DeriveError, match="inflate_to_year"):
        evaluate(room, _inflate_derived(), series)


def test_inflate_zero_base_raises() -> None:
    room = _room((_fact("us-2020s-base", 2736600),))
    series = _inflate_series({2020: 0.0, 2024: 100.0})
    with pytest.raises(DeriveError, match="zero"):
        evaluate(room, _inflate_derived(), series)
