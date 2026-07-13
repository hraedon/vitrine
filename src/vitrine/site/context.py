"""Frozen typed page and view models — the template boundary.

Every Jinja template receives a single ``page`` object (one of the ``*Page``
dataclasses below) carrying exactly what that surface needs to render. The
intermediate ``*View`` types are the structured shapes projections emit and
templates iterate. All are ``frozen=True, slots=True``; ordered collections are
``tuple``, lookup-only maps are ``Mapping`` — nothing mutable is advertised.

Globals (``disclaimer``, ``disclaimer_title``, ``T``, ``tier_names``,
``panel_title``, ``tier_label``, ``basis_label``) and the per-render
``root`` / ``surface`` params stay on the environment / render call, not on the
page.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from markupsafe import Markup

from vitrine.model import Assumption, Fact, Panel, Room, Source
from vitrine.site.curation import Metric
from vitrine.site.svg import ShareSegment

if TYPE_CHECKING:
    from vitrine.derive import ComputedFact


# ── fact reference (pairs a fact with its room for overlay placards) ──────────


@dataclass(frozen=True, slots=True)
class FactRef:
    """A fact paired with the room it belongs to (for overlay placards)."""

    room: Room
    fact: Fact


# ── room story & panels ───────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class RoomStoryView:
    """The curator's four-fact opening route through one decade room."""

    title: str
    question: str
    facts: tuple[Fact, ...]


@dataclass(frozen=True, slots=True)
class PanelSection:
    """One display case: its panel enum plus the sourced and computed facts."""

    panel: Panel
    facts: tuple[Fact, ...]
    computed: tuple[ComputedFact, ...]


# ── corridor atlas ────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class ArcSection:
    """One charted arc or arc-group in the corridor atlas directory."""

    slug: str
    label: str
    unit: str
    caveats: tuple[str, ...]
    coverage: str
    chart: Markup


@dataclass(frozen=True, slots=True)
class CorridorWingView:
    """An editorial chapter gathering arcs (and the economy portal)."""

    slug: str
    number: str
    title: str
    question: str
    introduction: str
    arcs: tuple[ArcSection, ...]
    exhibit_count: int


@dataclass(frozen=True, slots=True)
class CompositionRow:
    """A folded budget-composition bar for one decade."""

    bar: Markup
    decade: str
    fact_id: str
    segments: tuple[ShareSegment, ...]


# ── pairwise ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class PairCell:
    """One comparable value cell in a pairwise family or affordability table."""

    decade: str
    fact_id: str
    href: str
    overlay_href: str
    tier: str
    text: str
    gap: bool


@dataclass(frozen=True, slots=True)
class PairFamily:
    """A fact family the measure guard certifies comparable for a pair."""

    label: str
    unit: str
    caveats: tuple[str, ...]
    cells: tuple[PairCell, ...]


@dataclass(frozen=True, slots=True)
class PairAffordSection:
    """An affordability comparison row for a pair, or its documented gap."""

    label: str
    caveats: tuple[str, ...]
    rows: tuple[PairCell, ...]
    gap_reason: str = ""


# ── walkthrough ───────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class WalkthroughPersonRow:
    """One sourced record beneath a walkthrough figure."""

    fact_id: str
    href: str
    label: str
    value: str
    tier: str


@dataclass(frozen=True, slots=True)
class WalkthroughPerson:
    """One lens (paid/unpaid/childhood) at a walkthrough stop."""

    name: str
    fig: Markup
    rows: tuple[WalkthroughPersonRow, ...]


@dataclass(frozen=True, slots=True)
class WalkthroughStop:
    """One decade stop on the guided transect."""

    decade: str
    stage: Markup
    people: tuple[WalkthroughPerson, ...]


@dataclass(frozen=True, slots=True)
class WalkthroughMetricCell:
    """One cell in a walkthrough same-measure-across-stops row."""

    decade: str
    fact_id: str
    href: str
    tier: str
    gap: bool
    text: str
    bar: int


@dataclass(frozen=True, slots=True)
class WalkthroughMetric:
    """One measure traced across the three walkthrough stops."""

    label: str
    unit: str
    falling: bool
    cells: tuple[WalkthroughMetricCell, ...]


@dataclass(frozen=True, slots=True)
class WalkthroughHouse:
    """A true-scale (or reference-outline) house for one walkthrough stop."""

    decade: str
    fact_id: str
    href: str
    gap: bool
    w: int
    hgt: int
    path: str
    caption: str


# ── affordability dashboard ───────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class AffordabilityDashboardSection:
    """One computed metric chart (or its documented gap) on the dashboard."""

    metric: Metric
    chart: Markup
    note: str


# ── page contexts (one per template) ──────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class LobbyPage:
    """Context for ``index.html`` — the museum lobby / room directory."""

    rooms: tuple[Room, ...]


@dataclass(frozen=True, slots=True)
class RoomPage:
    """Context for ``room.html`` — one decade gallery."""

    room: Room
    rooms: tuple[Room, ...]
    story: RoomStoryView
    previous_room: Room | None
    next_room: Room | None
    room_position: int
    stage_svg: Markup
    panels: tuple[PanelSection, ...]
    computed_count: int
    sources: Mapping[str, Source]
    assumptions: Mapping[str, Assumption]
    affordability: Mapping[str, Mapping[str, str]]
    gap_banner: str


@dataclass(frozen=True, slots=True)
class CorridorPage:
    """Context for ``corridors/index.html`` — the four-wing atlas."""

    decades: tuple[str, ...]
    epochs: tuple[tuple[str, str], ...]
    pair_count: int
    wings: tuple[CorridorWingView, ...]
    afford_sections: tuple[ArcSection, ...]
    comp_rows: tuple[CompositionRow, ...]
    comp_caveats: tuple[str, ...]
    sources: Mapping[str, Source]
    assumptions: Mapping[str, Assumption]
    affordability: Mapping[str, Mapping[str, str]]
    overlay_facts: tuple[FactRef, ...]


@dataclass(frozen=True, slots=True)
class PairPage:
    """Context for ``corridors/<a>--<b>.html`` — a pairwise comparison."""

    a: str
    b: str
    families: tuple[PairFamily, ...]
    afford_sections: tuple[PairAffordSection, ...]
    comp_rows: tuple[CompositionRow, ...]
    sources: Mapping[str, Source]
    assumptions: Mapping[str, Assumption]
    affordability: Mapping[str, Mapping[str, str]]
    overlay_facts: tuple[FactRef, ...]


@dataclass(frozen=True, slots=True)
class AffordabilityPage:
    """Context for ``affordability/index.html`` — the annual ratios dashboard."""

    sections: tuple[AffordabilityDashboardSection, ...]
    recession_url: str


@dataclass(frozen=True, slots=True)
class WalkthroughPage:
    """Context for ``walkthrough.html`` — the guided three-stop transect."""

    stops: tuple[str, ...]
    stop_sections: tuple[WalkthroughStop, ...]
    metrics: tuple[WalkthroughMetric, ...]
    meter: Markup
    meter_caveats: tuple[str, ...]
    houses: tuple[WalkthroughHouse, ...]
    sources: Mapping[str, Source]
    assumptions: Mapping[str, Assumption]
    affordability: Mapping[str, Mapping[str, str]]
    overlay_facts: tuple[FactRef, ...]


@dataclass(frozen=True, slots=True)
class MethodologyPage:
    """Context for ``methodology.html`` — the assumption ledger."""

    assumptions: tuple[Assumption, ...]


@dataclass(frozen=True, slots=True)
class BibliographyPage:
    """Context for ``bibliography.html`` — the full source register."""

    sources: tuple[Source, ...]


# Re-exported so svg type references resolve cleanly from this module's namespace.
__all__ = [
    "AffordabilityDashboardSection",
    "AffordabilityPage",
    "ArcSection",
    "BibliographyPage",
    "CompositionRow",
    "CorridorPage",
    "CorridorWingView",
    "FactRef",
    "LobbyPage",
    "MethodologyPage",
    "PairAffordSection",
    "PairCell",
    "PairFamily",
    "PairPage",
    "PanelSection",
    "RoomPage",
    "RoomStoryView",
    "WalkthroughHouse",
    "WalkthroughMetric",
    "WalkthroughMetricCell",
    "WalkthroughPage",
    "WalkthroughPerson",
    "WalkthroughPersonRow",
    "WalkthroughStop",
]