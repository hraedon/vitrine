"""The provenance gate — referential invariants over a loaded corpus.

See docs/fact-model.md "Invariants". Structural validation (types, enum
values) already happened in the loader; this checks that every fact is
verifiable: sources resolve, assumptions resolve, ids are unique and honest,
and nothing verifiability-critical is blank.
"""

from __future__ import annotations

from vitrine.model import Corpus


def check_corpus(corpus: Corpus) -> list[str]:
    """Return all problems found; an empty list means the gate is green."""
    problems: list[str] = []

    for source in corpus.sources.values():
        if not source.url.strip():
            problems.append(f"source {source.id!r}: empty url — facts must be verifiable")
        if not source.population.strip():
            problems.append(f"source {source.id!r}: empty population — say who was measured")

    seen: dict[str, str] = {}
    for room in corpus.rooms:
        prefix = f"{room.country}-{room.decade}-"
        for fact in room.facts:
            where = f"room {room.slug}, fact {fact.id!r}"

            if fact.id in seen:
                problems.append(f"{where}: duplicate fact id (also in room {seen[fact.id]})")
            seen[fact.id] = room.slug

            if not fact.id.startswith(prefix):
                problems.append(f"{where}: id must start with {prefix!r}")

            if fact.source not in corpus.sources:
                problems.append(f"{where}: unknown source {fact.source!r}")

            for assumption_id in fact.assumptions:
                if assumption_id not in corpus.assumptions:
                    problems.append(f"{where}: unknown assumption {assumption_id!r}")

            for field_name, value in (
                ("label", fact.label),
                ("value", fact.value),
                ("unit", fact.unit),
            ):
                if not value.strip():
                    problems.append(f"{where}: empty {field_name}")

    return problems
