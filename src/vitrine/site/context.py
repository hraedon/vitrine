"""Typed page contexts — frozen, slotted dataclasses replacing dict view models.

Templates receive fully prepared values. They do not resolve fact IDs,
calculate ratios, or make comparability decisions.
"""

from __future__ import annotations

from dataclasses import dataclass

from vitrine.derive import ComputedFact
from vitrine.model import Assumption, Fact, Panel, Room, Source
from vitrine.site.curation.affordability import Metric
from vitrine.site.projections.facts import FactRef
from vitrine.site.projections.pairs import PairAffordSection, PairFamily
from vitrine.site.svg import ShareSegment

# ── shared view-model types ──────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class AffordabilityDisplay:
    hours: str
    hours_large: str
    pct: str
    tier: str
    anchor_note: str
    measures: str


@dataclass(frozen=True, slots=True)
class PanelSection:
    panel: Panel
    facts: list[Fact]
    computed: list[ComputedFact]


@dataclass(frozen=True, slots=True)
class ArcSection:
    slug: str
    label: str
    unit: str
    caveats: tuple[str, ...]
    chart: str


@dataclass(frozen=True, slots=True)
class CorridorAffordSection:
    label: str
    caveats: tuple[str, ...]
    chart: str


@dataclass(frozen=True, slots=True)
class CompositionRow:
    bar: str
    decade: str
    fact_id: str
    segments: tuple[ShareSegment, ...]


@dataclass(frozen=True, slots=True)
class WalkthroughPersonRow:
    fact_id: str
    href: str
    label: str
    value: str
    tier: str


@dataclass(frozen=True, slots=True)
class WalkthroughPerson:
    name: str
    fig: str
    rows: list[WalkthroughPersonRow]


@dataclass(frozen=True, slots=True)
class WalkthroughStop:
    decade: str
    stage: str
    people: list[WalkthroughPerson]


@dataclass(frozen=True, slots=True)
class WalkthroughMetricCell:
    decade: str
    fact_id: str
    href: str
    tier: str
    gap: bool
    text: str
    bar: int


@dataclass(frozen=True, slots=True)
class WalkthroughMetric:
    label: str
    unit: str
    falling: bool
    cells: list[WalkthroughMetricCell]


@dataclass(frozen=True, slots=True)
class WalkthroughHouse:
    decade: str
    fact_id: str
    href: str
    gap: bool
    w: int
    hgt: int
    path: str
    caption: str


@dataclass(frozen=True, slots=True)
class AffordabilityDashboardSection:
    metric: Metric
    chart: str
    note: str


# ── page contexts ─────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class LobbyContext:
    root: str
    rooms: list[Room]


@dataclass(frozen=True, slots=True)
class RoomContext:
    root: str
    room: Room
    rooms: list[Room]
    stage_svg: str
    panels: list[PanelSection]
    sources: dict[str, Source]
    assumptions: dict[str, Assumption]
    affordability: dict[str, dict[str, str]]
    gap_banner: str


@dataclass(frozen=True, slots=True)
class MethodologyContext:
    root: str
    assumptions: list[Assumption]


@dataclass(frozen=True, slots=True)
class BibliographyContext:
    root: str
    sources: list[Source]


@dataclass(frozen=True, slots=True)
class CorridorContext:
    root: str
    decades: list[str]
    epochs: list[tuple[str, str]]
    arc_sections: list[ArcSection]
    afford_sections: list[CorridorAffordSection]
    comp_rows: list[CompositionRow]
    comp_caveats: str
    sources: dict[str, Source]
    assumptions: dict[str, Assumption]
    affordability: dict[str, dict[str, str]]
    overlay_facts: tuple[FactRef, ...]


@dataclass(frozen=True, slots=True)
class PairContext:
    root: str
    a: str
    b: str
    families: list[PairFamily]
    afford_sections: list[PairAffordSection]
    comp_rows: list[CompositionRow]
    sources: dict[str, Source]
    assumptions: dict[str, Assumption]
    affordability: dict[str, dict[str, str]]
    overlay_facts: tuple[FactRef, ...]


@dataclass(frozen=True, slots=True)
class WalkthroughContext:
    root: str
    stops: list[str]
    stop_sections: list[WalkthroughStop]
    metrics: list[WalkthroughMetric]
    meter: str
    meter_caveats: tuple[str, ...]
    houses: list[WalkthroughHouse]
    sources: dict[str, Source]
    assumptions: dict[str, Assumption]
    affordability: dict[str, dict[str, str]]
    overlay_facts: tuple[FactRef, ...]


@dataclass(frozen=True, slots=True)
class AffordabilityContext:
    root: str
    sections: list[AffordabilityDashboardSection]
    disclaimer: str
    recession_url: str
