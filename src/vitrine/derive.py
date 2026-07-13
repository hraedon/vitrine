"""Evaluate derived facts — the derivation is code, never an authored number.

See plan 006. A ``DerivedFact`` authors structure (two operand fact ids and an
op); this module resolves the operands within the room (or across the corpus
for cross-room derived facts), computes the value, and computes the tier as
the weakest operand tier. The checker guarantees the operands resolve and are
structured before anything renders, so evaluation here can be strict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import assert_never

from vitrine.model import DerivedFact, DerivedOp, Fact, Panel, Room, Tier, weakest_tier
from vitrine.series import Series


@dataclass(frozen=True, slots=True)
class ComputedFact:
    """A DerivedFact evaluated against its room — display-ready."""

    id: str
    panel: Panel
    label: str
    unit: str
    value: str  # computed display string, e.g. "≈ 2.6"
    tier: Tier  # weakest operand tier — computed, never authored
    numerator: Fact
    denominator: Fact
    op: DerivedOp
    notes: str
    assumptions: tuple[str, ...]
    inflate_series: str = ""  # series id (INFLATE op only)
    inflate_from_year: int = 0  # base year (INFLATE op only)
    inflate_to_year: int = 0  # target year (INFLATE op only)


class DeriveError(Exception):
    """A derived fact's operands don't support evaluation.

    The checker reports these as gate failures before render; hitting this
    at render time means the gate was skipped.
    """


def _resolve_structured(
    room: Room, fact_id: str, ctx: str, fact_index: dict[str, Fact] | None = None
) -> Fact:
    """Resolve a fact id to a structured Fact, searching the room first then
    the cross-room fact index (if provided)."""
    for fact in room.facts:
        if fact.id == fact_id:
            return fact
    if fact_index is not None and fact_id in fact_index:
        return fact_index[fact_id]
    raise DeriveError(f"{ctx}: operand {fact_id!r} not found in room {room.slug}")


def _op_value(op: DerivedOp, ratio: float, precision: int) -> str:
    match op:
        case DerivedOp.RATIO:
            return f"≈ {ratio:,.{precision}f}"
        case DerivedOp.PCT_OF:
            return f"≈ {ratio * 100:,.{precision}f}%"
        case DerivedOp.INFLATE:
            return f"≈ ${ratio:,.{precision}f}"
        case DerivedOp.PRODUCT:
            return f"≈ ${ratio:,.{precision}f}"
        case DerivedOp.QUANTITY_RATIO:
            return f"≈ {ratio:,.{precision}f}"
        case _:
            assert_never(op)


def evaluate(
    room: Room,
    derived: DerivedFact,
    series: dict[str, Series] | None = None,
    fact_index: dict[str, Fact] | None = None,
) -> ComputedFact:
    """Compute one derived fact from its room's operands.

    ``fact_index`` enables cross-room operand resolution: if an operand is
    not in ``room``, it is looked up in the index (which spans the corpus).
    """
    ctx = f"derived {derived.id!r}"
    numerator = _resolve_structured(room, derived.numerator, ctx, fact_index)

    if derived.op is DerivedOp.INFLATE:
        if series is None or derived.inflate_series not in series:
            raise DeriveError(f"{ctx}: inflate_series {derived.inflate_series!r} not available")
        s = series[derived.inflate_series]
        vals = s.values_minor if s.values_minor else s.values
        from_year = derived.inflate_from_year
        to_year = derived.inflate_to_year
        if from_year not in vals:
            raise DeriveError(f"{ctx}: inflate_from_year {from_year} not in series")
        if to_year not in vals:
            raise DeriveError(f"{ctx}: inflate_to_year {to_year} not in series")
        base = vals[from_year]
        target = vals[to_year]
        if base == 0:
            raise DeriveError(f"{ctx}: inflate_from_year value is zero")
        assert numerator.amount_minor is not None
        inflated = numerator.amount_minor * target / base
        return ComputedFact(
            id=derived.id,
            panel=derived.panel,
            label=derived.label,
            unit=derived.unit,
            value=_op_value(derived.op, inflated / 100.0, derived.precision),
            tier=weakest_tier(numerator.tier, s.tier),  # weakest input — series too
            numerator=numerator,
            denominator=numerator,  # no denominator fact; self-reference for the type
            op=derived.op,
            notes=derived.notes,
            assumptions=derived.assumptions,
            inflate_series=derived.inflate_series,
            inflate_from_year=derived.inflate_from_year,
            inflate_to_year=derived.inflate_to_year,
        )

    denominator = _resolve_structured(room, derived.denominator, ctx, fact_index)

    if derived.op is DerivedOp.PRODUCT:
        if numerator.amount_minor is None:
            raise DeriveError(f"{ctx}: numerator {numerator.id!r} has no amount_minor")
        if denominator.quantity is None:
            raise DeriveError(f"{ctx}: denominator {denominator.id!r} has no quantity")
        product = numerator.amount_minor * denominator.quantity
        return ComputedFact(
            id=derived.id,
            panel=derived.panel,
            label=derived.label,
            unit=derived.unit,
            value=_op_value(derived.op, product / 100.0, derived.precision),
            tier=weakest_tier(numerator.tier, denominator.tier),
            numerator=numerator,
            denominator=denominator,
            op=derived.op,
            notes=derived.notes,
            assumptions=derived.assumptions,
        )

    if derived.op is DerivedOp.QUANTITY_RATIO:
        if numerator.quantity is None:
            raise DeriveError(f"{ctx}: numerator {numerator.id!r} has no quantity")
        if denominator.quantity is None:
            raise DeriveError(f"{ctx}: denominator {denominator.id!r} has no quantity")
        if denominator.quantity == 0:
            raise DeriveError(f"{ctx}: denominator {denominator.id!r} quantity is zero")
        ratio = numerator.quantity / denominator.quantity
        return ComputedFact(
            id=derived.id,
            panel=derived.panel,
            label=derived.label,
            unit=derived.unit,
            value=_op_value(derived.op, ratio, derived.precision),
            tier=weakest_tier(numerator.tier, denominator.tier),
            numerator=numerator,
            denominator=denominator,
            op=derived.op,
            notes=derived.notes,
            assumptions=derived.assumptions,
        )

    # RATIO and PCT_OF: both operands must be structured monetary facts
    if numerator.amount_minor is None:
        raise DeriveError(f"{ctx}: numerator {numerator.id!r} has no amount_minor")
    if denominator.amount_minor is None:
        raise DeriveError(f"{ctx}: denominator {denominator.id!r} has no amount_minor")
    if denominator.amount_minor == 0:
        raise DeriveError(f"{ctx}: denominator {denominator.id!r} is zero")
    if numerator.currency != denominator.currency:
        raise DeriveError(
            f"{ctx}: currency mismatch "
            f"({numerator.currency!r} vs {denominator.currency!r})"
        )

    ratio = numerator.amount_minor / denominator.amount_minor
    return ComputedFact(
        id=derived.id,
        panel=derived.panel,
        label=derived.label,
        unit=derived.unit,
        value=_op_value(derived.op, ratio, derived.precision),
        tier=weakest_tier(numerator.tier, denominator.tier),
        numerator=numerator,
        denominator=denominator,
        op=derived.op,
        notes=derived.notes,
        assumptions=derived.assumptions,
    )


def evaluate_room(
    room: Room,
    series: dict[str, Series] | None = None,
    fact_index: dict[str, Fact] | None = None,
) -> tuple[ComputedFact, ...]:
    """Evaluate every derived fact declared in a room."""
    return tuple(evaluate(room, d, series, fact_index) for d in room.derived)
