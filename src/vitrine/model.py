"""The normalized fact model — see docs/fact-model.md, the design spine.

Everything the site displays is a projection of these types. ``Tier`` and
``Panel`` are closed sets: every dispatch over them must end in
``typing.assert_never`` so that adding a variant breaks the build at each
unhandled site.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import assert_never


class Tier(enum.Enum):
    """Confidence tier for a fact."""

    A = "A"  # official statistical series for the stated population
    B = "B"  # official microdata; statistic computed by this project
    C = "C"  # reconstructed from contemporaneous surveys of a proxy population
    D = "D"  # scholarly estimate or narrative; no contemporaneous survey


class Panel(enum.Enum):
    """The six-panel room skeleton, identical in every room."""

    HOME = "home"
    BUDGET = "budget"
    TABLE = "table"
    DAY = "day"
    DIFFUSION = "diffusion"
    WORK_BUYS = "work-buys"


def tier_label(tier: Tier) -> str:
    """Visitor-facing description of a confidence tier."""
    match tier:
        case Tier.A:
            return "Official series"
        case Tier.B:
            return "Official microdata (computed)"
        case Tier.C:
            return "Reconstructed from period surveys"
        case Tier.D:
            return "Scholarly estimate"
        case _:
            assert_never(tier)


def panel_title(panel: Panel) -> str:
    """Visitor-facing title of a room panel."""
    match panel:
        case Panel.HOME:
            return "The home"
        case Panel.BUDGET:
            return "The budget"
        case Panel.TABLE:
            return "The table"
        case Panel.DAY:
            return "The day"
        case Panel.DIFFUSION:
            return "What had arrived"
        case Panel.WORK_BUYS:
            return "A day's work buys"
        case _:
            assert_never(panel)


@dataclass(frozen=True, slots=True)
class Source:
    """An entry in the global source registry (data/sources.toml)."""

    id: str
    title: str
    publisher: str
    year: int
    url: str
    population: str  # who was actually measured — the anti-composite field
    notes: str = ""


@dataclass(frozen=True, slots=True)
class Assumption:
    """An entry in the assumption ledger (data/assumptions.toml)."""

    id: str
    title: str
    statement: str


@dataclass(frozen=True, slots=True)
class Fact:
    """One claim, one source, one tier — the atomic exhibit unit."""

    id: str
    panel: Panel
    label: str
    value: str  # display value as authored; see fact-model.md on structured numerics
    unit: str
    source: str  # Source.id
    tier: Tier
    notes: str = ""
    assumptions: tuple[str, ...] = field(default=())


@dataclass(frozen=True, slots=True)
class Room:
    """One (country, decade) exhibit room."""

    country: str  # lowercase slug: us, uk, pl, ru, cn, in, jp
    decade: str  # "1890s" … "2020s"
    facts: tuple[Fact, ...]

    @property
    def slug(self) -> str:
        return f"{self.country}-{self.decade}"


@dataclass(frozen=True, slots=True)
class Corpus:
    """Everything under data/: the museum, before projection."""

    sources: dict[str, Source]
    assumptions: dict[str, Assumption]
    rooms: tuple[Room, ...]
