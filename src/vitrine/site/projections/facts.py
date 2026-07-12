"""Fact indexing and placard href helpers."""

from __future__ import annotations

from dataclasses import dataclass

from vitrine.model import Corpus, Fact, Room


@dataclass(frozen=True, slots=True)
class FactRef:
    room: Room
    fact: Fact


def index_facts(corpus: Corpus) -> dict[str, FactRef]:
    return {f.id: FactRef(room, f) for room in corpus.rooms for f in room.facts}


def placard_href(index: dict[str, FactRef], fact_id: str, root: str) -> str:
    ref = index[fact_id]
    return f"{root}rooms/{ref.room.slug}.html#{fact_id}"
