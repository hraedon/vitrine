"""Room projection — assembles a fully-prepared ``RoomPage`` for ``room.html``.

Owns the curator's opening-route story, the six display-case panels, the house
cutaway stage, and the per-room affordability display. All fact-id resolution,
SVG generation, and ratio computation happen here; the orchestrator only
renders and writes.
"""

from __future__ import annotations

from markupsafe import Markup

from vitrine.derive import ComputedFact, evaluate_room
from vitrine.model import Corpus, Panel, Room
from vitrine.series import Series
from vitrine.site import curation, svg
from vitrine.site.context import LobbyPage, PanelSection, RoomPage, RoomStoryView
from vitrine.site.projections.affordability import affordability_for_room
from vitrine.site.projections.facts import FactRef
from vitrine.site.projections.stage import build_stage


def room_story(room: Room) -> RoomStoryView:
    story = curation.ROOM_STORY_BY_DECADE.get(room.decade)
    if story is None:
        raise ValueError(f"room {room.decade} has no curated opening route")
    if any(character.isdigit() for character in story.title + story.question):
        raise ValueError(
            f"room {room.decade} story framing must not author historical numbers"
        )
    if len(story.fact_ids) != 4 or len(set(story.fact_ids)) != 4:
        raise ValueError(
            f"room {room.decade} story must name exactly four distinct facts"
        )
    facts_by_id = {fact.id: fact for fact in room.facts}
    missing = [fact_id for fact_id in story.fact_ids if fact_id not in facts_by_id]
    if missing:
        raise ValueError(
            f"room {room.decade} story names facts outside the room: {missing}"
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


def project_lobby(rooms: list[Room] | tuple[Room, ...]) -> LobbyPage:
    """Project the museum lobby / room directory."""
    return LobbyPage(rooms=tuple(rooms))


def project_room(
    corpus: Corpus,
    room: Room,
    rooms: list[Room] | tuple[Room, ...],
    room_position: int,
    index: dict[str, FactRef],
    series: dict[str, Series],
) -> RoomPage:
    """Project one room into a fully-prepared ``RoomPage``."""
    fact_index = {fid: ref.fact for fid, ref in index.items()}
    computed = evaluate_room(room, series, fact_index)
    affordability = affordability_for_room(corpus, room)
    stage = build_stage(room, index, "../")
    return RoomPage(
        room=room,
        rooms=tuple(rooms),
        story=room_story(room),
        previous_room=rooms[room_position - 2] if room_position > 1 else None,
        next_room=rooms[room_position] if room_position < len(rooms) else None,
        room_position=room_position,
        stage_svg=Markup(svg.stage_svg(stage, overlay_links=True)),
        panels=panels_for(room, computed),
        computed_count=len(computed),
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        affordability=affordability,
        gap_banner=curation.ROOM_GAP_BANNERS.get(room.decade, ""),
    )
