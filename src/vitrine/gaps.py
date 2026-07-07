"""Mechanical gap inventory — `vitrine gaps`.

The gap log is generated from the corpus, never hand-maintained: a
hand-maintained summary table drifting out of sync with the data it
summarizes is this project's founding observation about everyone else's
history content, and it happened to our own docs/gap-log.md within a week.

Classification is mechanical:

- **rendered gap** — the fact's honest value is that no record exists
  (``value`` starts with "no reliable record"); the visitor sees the gap.
- **Tier D estimate** — a displayed value whose source is a scholarly
  estimate or secondary narrative; candidate for a primary-source upgrade.
- **empty panel** — a room panel with no facts at all ("Not yet curated"
  in the rendered room).

Anything softer (which primary source would fill a gap, which gaps are
permanent) is curator commentary and lives in docs/gap-log.md prose.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import assert_never

from vitrine.model import Corpus, Panel, Tier

_GAP_VALUE_PREFIX = "no reliable record"


class GapKind(enum.Enum):
    """Why a fact appears in the gap inventory — closed set."""

    RENDERED_GAP = "rendered-gap"
    TIER_D_ESTIMATE = "tier-d-estimate"


def gap_kind_label(kind: GapKind) -> str:
    """Report heading for a gap kind."""
    match kind:
        case GapKind.RENDERED_GAP:
            return "rendered gaps (no reliable record)"
        case GapKind.TIER_D_ESTIMATE:
            return "Tier D estimates (displayed value, upgrade candidates)"
        case _:
            assert_never(kind)


@dataclass(frozen=True, slots=True)
class RoomGaps:
    """The gap inventory for one room."""

    slug: str
    rendered_gaps: tuple[str, ...]  # fact ids
    tier_d_estimates: tuple[str, ...]  # fact ids
    empty_panels: tuple[Panel, ...]
    n_facts: int
    n_tier_a: int


def room_gaps(corpus: Corpus) -> tuple[RoomGaps, ...]:
    """Classify every room's gaps from the corpus alone."""
    result: list[RoomGaps] = []
    for room in corpus.rooms:
        rendered: list[str] = []
        estimates: list[str] = []
        for fact in room.facts:
            if fact.value.strip().lower().startswith(_GAP_VALUE_PREFIX):
                rendered.append(fact.id)
            elif fact.tier is Tier.D:
                estimates.append(fact.id)
        populated = {fact.panel for fact in room.facts}
        result.append(
            RoomGaps(
                slug=room.slug,
                rendered_gaps=tuple(rendered),
                tier_d_estimates=tuple(estimates),
                empty_panels=tuple(p for p in Panel if p not in populated),
                n_facts=len(room.facts),
                n_tier_a=sum(1 for f in room.facts if f.tier is Tier.A),
            )
        )
    return tuple(result)


def format_report(rooms: tuple[RoomGaps, ...]) -> str:
    """Human-readable inventory, one block per room plus totals."""
    lines: list[str] = []
    total_gaps = total_estimates = total_empty = 0
    for rg in rooms:
        lines.append(
            f"{rg.slug}: {rg.n_facts} facts ({rg.n_tier_a} Tier A), "
            f"{len(rg.rendered_gaps)} rendered gap(s), "
            f"{len(rg.tier_d_estimates)} Tier D estimate(s), "
            f"{len(rg.empty_panels)} empty panel(s)"
        )
        for fid in rg.rendered_gaps:
            lines.append(f"  gap:      {fid}")
        for fid in rg.tier_d_estimates:
            lines.append(f"  estimate: {fid}")
        for panel in rg.empty_panels:
            lines.append(f"  empty:    {panel.value}")
        total_gaps += len(rg.rendered_gaps)
        total_estimates += len(rg.tier_d_estimates)
        total_empty += len(rg.empty_panels)
    lines.append(
        f"total: {sum(rg.n_facts for rg in rooms)} facts across {len(rooms)} rooms — "
        f"{total_gaps} rendered gap(s), {total_estimates} Tier D estimate(s), "
        f"{total_empty} empty panel(s)"
    )
    return "\n".join(lines)
