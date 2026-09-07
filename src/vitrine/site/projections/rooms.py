"""Room projection — assembles a fully-prepared ``RoomPage`` for ``room.html``.

Owns the curator's opening-route story, the six display-case panels, the house
cutaway stage, and the per-room affordability display. All fact-id resolution,
SVG generation, and ratio computation happen here; the orchestrator only
renders and writes.
"""

from __future__ import annotations

from markupsafe import Markup

from vitrine.derive import ComputedFact, evaluate_room
from vitrine.model import Corpus, Fact, Panel, Room, Tier
from vitrine.series import Series
from vitrine.site import curation, svg
from vitrine.site.context import (
    EssayEntryView,
    EssayLink,
    LobbyPage,
    MatrixCell,
    MatrixRow,
    PanelSection,
    RoomPage,
    RoomStoryView,
    WingView,
)
from vitrine.site.projections.affordability import affordability_for_room
from vitrine.site.projections.facts import GAP_PREFIX, FactRef
from vitrine.site.projections.stage import build_stage


def room_story(room: Room) -> RoomStoryView | None:
    """The curated opening route for *room*, or None if it has none.

    A room without a story is not an error: the v2 world-rooms program lands a
    country's data before its editorial layer, and an un-curated room renders a
    bare stage rather than blocking the build. What remains an error is a story
    that exists but does not hold up -- framing that authors its own numbers, a
    route that is not four distinct facts, or a fact borrowed from another room.
    """

    story = curation.ROOM_STORY_BY_SLUG.get(room.slug)
    if story is None:
        return None
    if any(character.isdigit() for character in story.title + story.question):
        raise ValueError(
            f"room {room.slug} story framing must not author historical numbers"
        )
    if len(story.fact_ids) != 4 or len(set(story.fact_ids)) != 4:
        raise ValueError(
            f"room {room.slug} story must name exactly four distinct facts"
        )
    facts_by_id = {fact.id: fact for fact in room.facts}
    missing = [fact_id for fact_id in story.fact_ids if fact_id not in facts_by_id]
    if missing:
        raise ValueError(
            f"room {room.slug} story names facts outside the room: {missing}"
        )
    return RoomStoryView(
        title=story.title,
        question=story.question,
        facts=tuple(facts_by_id[fact_id] for fact_id in story.fact_ids),
    )


def panels_for(
    room: Room, computed: tuple[ComputedFact, ...]
) -> tuple[PanelSection, ...]:
    """Group a room's sourced and computed facts by display-case panel."""
    return tuple(
        PanelSection(
            panel=panel,
            facts=tuple(f for f in room.facts if f.panel is panel),
            computed=tuple(c for c in computed if c.panel is panel),
        )
        for panel in Panel
    )


def _matrix_cell(facts: list[Fact], computed: list[ComputedFact]) -> MatrixCell:
    """Count one (room, panel) slot into an immutable ``MatrixCell``."""
    tier_counts = tuple(
        (tier.value, sum(1 for f in facts if f.tier is tier))
        for tier in Tier
    )
    return MatrixCell(
        facts=len(facts),
        computed=len(computed),
        gaps=sum(
            1 for f in facts if f.value.strip().lower().startswith(GAP_PREFIX)
        ),
        tier_counts=tuple(entry for entry in tier_counts if entry[1]),
    )


def atlas_matrix(
    rooms: tuple[Room, ...],
    computed_by_room: dict[str, tuple[ComputedFact, ...]],
) -> tuple[tuple[MatrixRow, ...], MatrixCell]:
    """The record at a glance: exhibit counts per (room, panel) and totals.

    Pure corpus metadata — the counts let the index render the corpus's
    honest shape (depth, tier mix, and the silences) without a visitor
    leaving the first page. Derived exhibits count separately; gaps are
    counted among the curated facts, exactly as the placard classifies them.
    """
    rows: list[MatrixRow] = []
    all_facts: list[Fact] = []
    all_computed: list[ComputedFact] = []
    for room in rooms:
        computed = list(computed_by_room.get(room.slug, ()))
        cells = tuple(
            _matrix_cell(
                [f for f in room.facts if f.panel is panel],
                [c for c in computed if c.panel is panel],
            )
            for panel in Panel
        )
        rows.append(
            MatrixRow(
                decade=room.decade,
                slug=room.slug,
                cells=cells,
                totals=_matrix_cell(list(room.facts), computed),
            )
        )
        all_facts.extend(room.facts)
        all_computed.extend(computed)
    return tuple(rows), _matrix_cell(all_facts, all_computed)


def project_lobby(
    corpus: Corpus,
    rooms: list[Room] | tuple[Room, ...],
    computed_by_room: dict[str, tuple[ComputedFact, ...]],
    essays: tuple[EssayEntryView, ...] = (),
    all_rooms: tuple[Room, ...] | None = None,
    curated_countries: frozenset[str] | set[str] = frozenset(),
) -> LobbyPage:
    """Project the atlas index / corpus directory.

    ``rooms`` is the curated set the comparative surfaces (matrix, ways in,
    room map) project over; ``all_rooms`` is the full corpus, from which the
    wing directory is derived so un-curated countries stay discoverable.
    """
    wings: tuple[WingView, ...] = ()
    if all_rooms:
        wings = tuple(
            WingView(
                country=country,
                rooms=wing_rooms,
                curated=country in curated_countries,
                facts=sum(len(room.facts) for room in wing_rooms),
            )
            for country in sorted(
                {room.country for room in all_rooms},
                key=lambda country: (country not in curated_countries, country),
            )
            for wing_rooms in (
                tuple(room for room in all_rooms if room.country == country),
            )
        )
    matrix, totals = atlas_matrix(tuple(rooms), computed_by_room)
    panel_totals = tuple(
        _matrix_cell(
            [f for room in rooms for f in room.facts if f.panel is panel],
            [
                c
                for room in rooms
                for c in computed_by_room.get(room.slug, ())
                if c.panel is panel
            ],
        )
        for panel in Panel
    )
    return LobbyPage(
        rooms=tuple(rooms),
        matrix=matrix,
        panel_totals=panel_totals,
        totals=totals,
        sources=len(corpus.sources),
        corpus_totals=_matrix_cell(
            [fact for room in corpus.rooms for fact in room.facts],
            [c for room in corpus.rooms for c in computed_by_room.get(room.slug, ())],
        ),
        essays=essays,
        wings=wings,
    )


def project_room(
    corpus: Corpus,
    room: Room,
    rooms: list[Room] | tuple[Room, ...],
    room_position: int,
    index: dict[str, FactRef],
    series: dict[str, Series],
    computed: tuple[ComputedFact, ...] | None = None,
    essay_links: tuple[EssayLink, ...] = (),
) -> RoomPage:
    """Project one room into a fully-prepared ``RoomPage``."""
    if computed is None:
        fact_index = {fid: ref.fact for fid, ref in index.items()}
        computed = evaluate_room(room, series, fact_index)
    affordability = affordability_for_room(corpus, room)
    stage = build_stage(room, index, "../")
    comparative = room.country in curation.CURATED_COUNTRIES
    return RoomPage(
        room=room,
        rooms=tuple(rooms),
        story=room_story(room),
        previous_room=rooms[room_position - 2] if room_position > 1 else None,
        next_room=rooms[room_position] if room_position < len(rooms) else None,
        room_position=room_position,
        stage_svg=Markup(svg.stage_svg(stage, overlay_links=True)),
        panels=panels_for(room, computed),
        essay_links=essay_links,
        computed_count=len(computed),
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        affordability=affordability,
        gap_banner=(
            curation.ROOM_GAP_BANNERS.get(room.decade, "") if comparative else ""
        ),
        comparative=comparative,
    )
