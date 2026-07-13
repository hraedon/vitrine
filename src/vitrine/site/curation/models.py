"""Curation registry models — the frozen editorial dataclasses.

Structure only: which fact ids form an arc, which glyph maps to which fact,
which four exhibits open a room. Values, tiers and geometry all come from the
corpus at build time.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Arc:
    """One cross-decade fact family, charted in the corridors."""

    slug: str
    label: str
    unit: str
    fact_ids: dict[str, str]  # decade → fact id
    falling: bool = False  # falling metrics render in copper
    caveats: tuple[str, ...] = field(default=())
    series_id: str = ""  # plan 010: annual series backing this arc, if any
    # A fact may have an honest quantity that is not comparable on this arc's
    # axis.  Keep the fact in the registry (and render a linked gap mark), but
    # never turn that quantity into geometry.  This is distinct from a fact
    # whose quantity is absent: the source has a number; the chart refuses the
    # splice.
    plot_gaps: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class ArcGroup:
    """Several related arcs rendered on one shared axis."""

    slug: str
    label: str
    unit: str
    members: tuple[tuple[str, str, str], ...]  # (arc slug, legend label, color role)
    caveats: tuple[str, ...] = field(default=())


@dataclass(frozen=True, slots=True)
class CorridorWing:
    """An editorial chapter in the corridor atlas.

    Wings arrange existing charts; they never introduce facts or geometry.
    ``arc_slugs`` names rendered arcs (including shared-axis group slugs).
    """

    slug: str
    number: str
    title: str
    question: str
    introduction: str
    arc_slugs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RoomStory:
    """A provenance-bound editorial route through one decade room.

    Titles and questions provide the lens; every exhibit displayed beneath
    them is an existing fact from that same room. The renderer validates the
    membership before building, so interpretation cannot borrow a foreign or
    unresolved exhibit.
    """

    decade: str
    title: str
    question: str
    fact_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Metric:
    """One affordability metric on the dashboard — a computed ratio over time.

    Ratio mode: ``numerator`` / ``denominator`` (each a tuple of series ids
    whose values merge; monetary series convert cents→dollars uniformly). A
    ``base_year`` re-scales the ratio so that year = 100 (an index).
    Direct mode: ``source_arc`` names an arc whose decade quantities plot
    as-is (for metrics with no annual series, e.g. food share).
    """

    slug: str
    label: str
    unit: str
    caption: str
    caveats: tuple[str, ...] = field(default=())
    numerator: tuple[str, ...] = field(default=())  # series ids (ratio mode)
    denominator: tuple[str, ...] = field(default=())  # series ids (ratio mode)
    numerator_scale: float = 1.0  # e.g. 52 for weekly→annual
    base_year: int | None = None  # if set, ratio normalized to 100 at this year
    percent: bool = False  # if True, ratio x 100 (share-of metrics)
    source_arc: str = ""  # arc slug whose decade quantities plot directly
    falling: bool = False  # falling metrics render in copper
    zero_baseline: bool = True  # False only for indices where zero has no meaning
