"""Evaluate derived facts — the derivation is code, never an authored number.

See plan 006. A ``DerivedFact`` authors structure (two operand fact ids and an
op); this module resolves the operands within the room, computes the value,
and computes the tier as the weakest operand tier. The checker guarantees the
operands resolve and are structured before anything renders, so evaluation
here can be strict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import assert_never

from vitrine.model import DerivedFact, DerivedOp, Fact, Panel, Room, Tier, weakest_tier


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


class DeriveError(Exception):
    """A derived fact's operands don't support evaluation.

    The checker reports these as gate failures before render; hitting this
    at render time means the gate was skipped.
    """


def _resolve_structured(room: Room, fact_id: str, ctx: str) -> Fact:
    for fact in room.facts:
        if fact.id == fact_id:
            if fact.amount_minor is None:
                raise DeriveError(f"{ctx}: operand {fact_id!r} has no amount_minor")
            return fact
    raise DeriveError(f"{ctx}: operand {fact_id!r} not found in room {room.slug}")


def _op_value(op: DerivedOp, ratio: float, precision: int) -> str:
    match op:
        case DerivedOp.RATIO:
            return f"≈ {ratio:,.{precision}f}"
        case DerivedOp.PCT_OF:
            return f"≈ {ratio * 100:,.{precision}f}%"
        case _:
            assert_never(op)


def evaluate(room: Room, derived: DerivedFact) -> ComputedFact:
    """Compute one derived fact from its room's operands."""
    ctx = f"derived {derived.id!r}"
    numerator = _resolve_structured(room, derived.numerator, ctx)
    denominator = _resolve_structured(room, derived.denominator, ctx)
    assert numerator.amount_minor is not None  # _resolve_structured guarantees
    assert denominator.amount_minor is not None
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


def evaluate_room(room: Room) -> tuple[ComputedFact, ...]:
    """Evaluate every derived fact declared in a room."""
    return tuple(evaluate(room, d) for d in room.derived)
