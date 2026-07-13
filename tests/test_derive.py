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


def _write_corpus_with_product(tmp_path: Path, valid: bool = True) -> Path:
    (tmp_path / "sources.toml").write_text(
        '[[source]]\nid = "src-1"\ntitle = "T"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "all families"\n'
    )
    (tmp_path / "assumptions.toml").write_text(
        '[[assumption]]\nid = "composite-family"\ntitle = "A"\nstatement = "S"\n'
    )
    room_dir = tmp_path / "us"
    room_dir.mkdir()
    hours_line = 'quantity = 40.5\n' if valid else ''
    (room_dir / "1950s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n'
        '[[fact]]\nid = "us-1950s-wage"\npanel = "day"\nlabel = "W"\nvalue = "$1.32"\n'
        'unit = "U"\nsource = "src-1"\ntier = "A"\namount_minor = 132\n'
        'currency = "USD"\nprice_year = 1950\nbasis = "hourly"\n\n'
        '[[fact]]\nid = "us-1950s-hours"\npanel = "day"\nlabel = "H"\nvalue = "40.5"\n'
        'unit = "hours"\nsource = "src-1"\ntier = "A"\n'
        f'{hours_line}'
        '[[derived]]\nid = "us-1950s-weekly-earnings"\npanel = "day"\nlabel = "D"\n'
        'unit = "USD"\nop = "product"\nnumerator = "us-1950s-wage"\n'
        'denominator = "us-1950s-hours"\n'
    )
    return tmp_path


def test_gate_flags_product_missing_quantity(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_product(tmp_path, valid=False))
    problems = check_corpus(corpus)
    assert any("us-1950s-hours" in p and "no quantity" in p for p in problems)


def test_gate_green_on_valid_product(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_product(tmp_path, valid=True))
    assert check_corpus(corpus) == []


def _write_corpus_with_qty_ratio(tmp_path: Path, valid: bool = True) -> Path:
    (tmp_path / "sources.toml").write_text(
        '[[source]]\nid = "src-1"\ntitle = "T"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "all families"\n'
    )
    (tmp_path / "assumptions.toml").write_text(
        '[[assumption]]\nid = "composite-family"\ntitle = "A"\nstatement = "S"\n'
    )
    room_dir = tmp_path / "us"
    room_dir.mkdir()
    qty_line = 'quantity = 24.1\n' if valid else ''
    (room_dir / "1950s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n'
        '[[fact]]\nid = "us-1950s-cpi"\npanel = "work-buys"\nlabel = "C"\n'
        'value = "24.1"\nunit = "index"\nsource = "src-1"\ntier = "A"\n'
        f'{qty_line}'
        '[[derived]]\nid = "us-1950s-purchasing-power"\npanel = "work-buys"\n'
        'label = "P"\nunit = "ratio"\nop = "quantity_ratio"\n'
        'numerator = "us-1950s-cpi"\ndenominator = "us-1950s-cpi"\n'
    )
    return tmp_path


def test_gate_flags_qty_ratio_missing_quantity(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_qty_ratio(tmp_path, valid=False))
    problems = check_corpus(corpus)
    assert any("us-1950s-cpi" in p and "no quantity" in p for p in problems)


def test_gate_green_on_valid_qty_ratio(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_qty_ratio(tmp_path, valid=True))
    assert check_corpus(corpus) == []


def _write_corpus_with_cross_room(tmp_path: Path, valid: bool = True) -> Path:
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
        '[[fact]]\nid = "us-1950s-cpi"\npanel = "work-buys"\nlabel = "C"\n'
        'value = "24.1"\nunit = "index"\nsource = "src-1"\ntier = "A"\n'
        'quantity = 24.1\n'
    )
    (room_dir / "2020s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "2020s"\n\n'
        '[[fact]]\nid = "us-2020s-cpi"\npanel = "work-buys"\nlabel = "C"\n'
        'value = "313.7"\nunit = "index"\nsource = "src-1"\ntier = "A"\n'
        'quantity = 313.7\n\n'
        '[[derived]]\nid = "us-2020s-purchasing-power"\npanel = "work-buys"\n'
        'label = "P"\nunit = "ratio"\nop = "quantity_ratio"\n'
        f'numerator = "us-2020s-cpi"\n'
        f'denominator = "{"us-1950s-cpi" if valid else "us-1950s-nope"}"\n'
    )
    return tmp_path


def test_gate_flags_cross_room_dangling_operand(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_cross_room(tmp_path, valid=False))
    problems = check_corpus(corpus)
    assert any("us-1950s-nope" in p and "does not resolve" in p for p in problems)


def test_gate_green_on_valid_cross_room(tmp_path: Path) -> None:
    corpus = load_corpus(_write_corpus_with_cross_room(tmp_path, valid=True))
    assert check_corpus(corpus) == []


def test_committed_corpus_derived_all_evaluate() -> None:
    from vitrine.series import load_series

    corpus = load_corpus(DATA)
    series = load_series(DATA)
    fact_index = {f.id: f for room in corpus.rooms for f in room.facts}
    n = 0
    for room in corpus.rooms:
        n += len(evaluate_room(room, series, fact_index))
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


# ── PRODUCT op (WI-5): monetary x quantity → monetary ──────────────────────


def _hours_fact(fact_id: str, hours: float, tier: Tier = Tier.A) -> Fact:
    return Fact(
        id=fact_id,
        panel=Panel.DAY,
        label="Weekly hours",
        value=str(hours),
        unit="hours per week",
        source="src-1",
        tier=tier,
        quantity=hours,
    )


def _product_derived(
    numerator_id: str = "us-1950s-wage", denominator_id: str = "us-1950s-hours"
) -> DerivedFact:
    return DerivedFact(
        id="us-1950s-weekly-earnings",
        panel=Panel.DAY,
        label="Weekly earnings",
        unit="USD per week",
        op=DerivedOp.PRODUCT,
        numerator=numerator_id,
        denominator=denominator_id,
        precision=2,
    )


def test_product_computes_correct_value() -> None:
    """$1.32 (132 cents) x 40.5 hours = $53.46."""
    room = _room((
        _fact("us-1950s-wage", 132, Tier.A),
        _hours_fact("us-1950s-hours", 40.5),
    ))
    computed = evaluate(room, _product_derived())
    assert computed.value == "≈ $53.46"
    assert computed.tier is Tier.A


def test_product_tier_is_weakest_input() -> None:
    room = _room((
        _fact("us-1950s-wage", 132, Tier.A),
        _hours_fact("us-1950s-hours", 40.5, Tier.C),
    ))
    computed = evaluate(room, _product_derived())
    assert computed.tier is Tier.C


def test_product_missing_quantity_raises() -> None:
    room = _room((
        _fact("us-1950s-wage", 132),
        _fact("us-1950s-hours", None),  # no amount_minor, no quantity
    ))
    with pytest.raises(DeriveError, match="no quantity"):
        evaluate(room, _product_derived())


# ── QUANTITY_RATIO op (WI-5): quantity / quantity → ratio ─────────────────


def _quantity_fact(fact_id: str, value: float, tier: Tier = Tier.A) -> Fact:
    return Fact(
        id=fact_id,
        panel=Panel.WORK_BUYS,
        label="CPI",
        value=str(value),
        unit="index",
        source="src-1",
        tier=tier,
        quantity=value,
    )


def _qty_ratio_derived() -> DerivedFact:
    return DerivedFact(
        id="us-1950s-purchasing-power",
        panel=Panel.WORK_BUYS,
        label="Purchasing power",
        unit="CPI ratio",
        op=DerivedOp.QUANTITY_RATIO,
        numerator="us-2020s-cpi",
        denominator="us-1950s-cpi",
        precision=2,
    )


def test_quantity_ratio_computes_correct_value() -> None:
    """313.7 / 24.1 = 13.02 (the old authored value '13.03' was slightly wrong)."""
    room = _room((_quantity_fact("us-1950s-cpi", 24.1),))
    fact_index = {"us-2020s-cpi": _quantity_fact("us-2020s-cpi", 313.7)}
    computed = evaluate(room, _qty_ratio_derived(), fact_index=fact_index)
    assert computed.value == "≈ 13.02"
    assert computed.tier is Tier.A


def test_quantity_ratio_cross_room_denominator() -> None:
    """Cross-room: numerator in the room, denominator in the index."""
    room = _room((_quantity_fact("us-2020s-cpi", 313.7),))
    fact_index = {"us-1950s-cpi": _quantity_fact("us-1950s-cpi", 24.1)}
    derived = DerivedFact(
        id="us-2020s-purchasing-power",
        panel=Panel.WORK_BUYS,
        label="Purchasing power",
        unit="CPI ratio",
        op=DerivedOp.QUANTITY_RATIO,
        numerator="us-2020s-cpi",
        denominator="us-1950s-cpi",
        precision=2,
    )
    computed = evaluate(room, derived, fact_index=fact_index)
    assert computed.value == "≈ 13.02"


def test_quantity_ratio_zero_denominator_raises() -> None:
    room = _room((_quantity_fact("us-1950s-cpi", 0.0),))
    fact_index = {"us-2020s-cpi": _quantity_fact("us-2020s-cpi", 313.7)}
    with pytest.raises(DeriveError, match="quantity is zero"):
        evaluate(room, _qty_ratio_derived(), fact_index=fact_index)


# ── Cross-room RATIO (WI-5): real-income-growth ────────────────────────────


def test_cross_room_ratio_computes_correct_value() -> None:
    """$105,800 / $35,290 = 3.0 (real income growth)."""
    room = _room((_fact("us-2020s-income", 10580000, Tier.A),))
    fact_index = {"us-1950s-real-income": _fact("us-1950s-real-income", 3529000, Tier.A)}
    derived = DerivedFact(
        id="us-2020s-real-income-growth",
        panel=Panel.WORK_BUYS,
        label="Real income growth",
        unit="ratio",
        op=DerivedOp.RATIO,
        numerator="us-2020s-income",
        denominator="us-1950s-real-income",
        precision=1,
    )
    computed = evaluate(room, derived, fact_index=fact_index)
    assert computed.value == "≈ 3.0"
    assert computed.tier is Tier.A
