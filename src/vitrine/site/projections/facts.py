"""Fact-index primitives shared across every surface projection.

``index_facts`` builds the global fact-id → ``FactRef`` lookup once per build;
``placard_href`` and ``overlay_facts`` are the single source for how a fact id
becomes a room-anchored URL or an overlay-deck ref list. ``FactRef`` itself
lives in ``context.py`` (the boundary layer) so the projections package can
import it without a cycle through this module's ``__init__``.
"""

from __future__ import annotations

from vitrine.model import Corpus
from vitrine.site.context import FactRef

GAP_PREFIX = "no reliable record"


def index_facts(corpus: Corpus) -> dict[str, FactRef]:
    """Global fact-id → (room, fact) lookup, built once per build."""
    return {f.id: FactRef(room, f) for room in corpus.rooms for f in room.facts}


def placard_href(index: dict[str, FactRef], fact_id: str, root: str) -> str:
    """The room-placard URL for ``fact_id`` under the given ``root`` prefix."""
    ref = index[fact_id]
    return f"{root}rooms/{ref.room.slug}.html#{fact_id}"


def overlay_facts(
    index: dict[str, FactRef], fact_ids: tuple[str, ...]
) -> tuple[FactRef, ...]:
    """Unique fact refs for the popup placard layer on corridor/pair pages."""
    seen: set[str] = set()
    refs: list[FactRef] = []
    for fid in fact_ids:
        if fid in seen or fid not in index:
            continue
        seen.add(fid)
        refs.append(index[fid])
    return tuple(refs)


__all__ = ["GAP_PREFIX", "FactRef", "index_facts", "overlay_facts", "placard_href"]
