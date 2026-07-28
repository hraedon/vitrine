"""Canonical corpus statistics — the numbers the README quotes, computed.

The README's Status section quotes corpus counts, and hand-kept counts drift
(this project's founding observation about everyone else's summaries, see
gaps.py, repeated for our own README status line by 2026-07). This module
computes the canonical numbers from the loaded corpus; the README carries
them in a marked block that ``tests/test_docs_sync.py`` verifies on every CI
run, and ``scripts/sync_readme_status.py`` regenerates the block in place.
"""

from __future__ import annotations

from dataclasses import dataclass

from vitrine.gaps import room_gaps
from vitrine.model import Corpus

README_BEGIN = "<!-- corpus-status:begin -->"
README_END = "<!-- corpus-status:end -->"


@dataclass(frozen=True, slots=True)
class CorpusStats:
    """The machine-checked counts quoted in the README Status section."""

    rooms: int
    facts: int
    derived: int
    tier_d_estimates: int
    rendered_gaps: int
    decade_span: str  # e.g. "1900s–2020s"


def corpus_stats(corpus: Corpus) -> CorpusStats:
    """Compute the canonical counts from a loaded corpus."""
    gaps = room_gaps(corpus)
    decades = sorted(room.decade for room in corpus.rooms)
    span = f"{decades[0]}–{decades[-1]}" if len(decades) > 1 else decades[0]
    return CorpusStats(
        rooms=len(corpus.rooms),
        facts=sum(len(room.facts) for room in corpus.rooms),
        derived=sum(len(room.derived) for room in corpus.rooms),
        tier_d_estimates=sum(len(rg.tier_d_estimates) for rg in gaps),
        rendered_gaps=sum(len(rg.rendered_gaps) for rg in gaps),
        decade_span=span,
    )


def render_status_line(stats: CorpusStats) -> str:
    """The canonical one-line status block quoted between the README markers."""
    return (
        f"{stats.rooms} decade rooms ({stats.decade_span}), "
        f"{stats.facts} facts, {stats.derived} derived facts, "
        f"{stats.tier_d_estimates} Tier D estimates, "
        f"{stats.rendered_gaps} rendered gaps"
    )


def _normalize(text: str) -> str:
    """Collapse whitespace runs so README line-wrapping is not load-bearing."""
    return " ".join(text.split())


def extract_status_block(readme_text: str) -> str | None:
    """The marked status block (whitespace-normalized), or None if unmarked."""
    begin = readme_text.find(README_BEGIN)
    end = readme_text.find(README_END)
    if begin == -1 or end == -1 or end < begin:
        return None
    return _normalize(readme_text[begin + len(README_BEGIN) : end])
