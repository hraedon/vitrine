"""Deterministic corpus exports for the archive wing.

The JSON export is a versioned projection of the loaded fact model.  It keeps
the authored derivation structure next to the computed value so consumers can
cite a result without losing the arithmetic that produced it.  The raw CSV
export is intentionally narrower: it contains only quantified, authored facts
and preserves machine values exactly.  The public ``facts.csv`` projection is
spreadsheet-safe and prefixes formula-like text with an apostrophe;
``facts-raw.csv`` is available when exact CSV values are needed.

This module is part of the stdlib-only core.  The site layer owns the HTML
landing page; JSON and CSV generation do not require the ``[site]`` extra.
"""

from __future__ import annotations

import csv
import io
import json
import math
from collections.abc import Mapping
from pathlib import Path

from vitrine.derive import ComputedFact, evaluate_room
from vitrine.model import Assumption, Corpus, DerivedFact, DerivedOp, Fact, Room, Source
from vitrine.publish import (
    OutputError,
    ensure_publishable_directory,
    staged_directory,
    validate_destination,
)
from vitrine.series import Series

SCHEMA_VERSION = 1
RAW_CSV_FILENAME = "facts-raw.csv"
SAFE_CSV_FILENAME = "facts.csv"
CSV_FIELDS = (
    "id",
    "decade",
    "panel",
    "label",
    "value",
    "quantity",
    "unit",
    "tier",
    "source_id",
    "short_cite",
)
_FORMULA_PREFIXES = ("=", "+", "-", "@")


def _source_payload(source: Source) -> dict[str, object]:
    """Serialize one source with every field in the normalized model."""
    return {
        "id": source.id,
        "title": source.title,
        "publisher": source.publisher,
        "year": source.year,
        "url": source.url,
        "population": source.population,
        "notes": source.notes,
        "short_cite": source.short_cite,
        "measure": source.measure.value if source.measure is not None else None,
        "expect": list(source.expect),
    }


def _assumption_payload(assumption: Assumption) -> dict[str, object]:
    """Serialize one assumption-ledger entry with every model field."""
    return {
        "id": assumption.id,
        "title": assumption.title,
        "statement": assumption.statement,
    }


def _series_payload(series: Series) -> dict[str, object]:
    """Serialize a complete annual series, including its observations."""
    return {
        "id": series.id,
        "label": series.label,
        "source": series.source,
        "tier": series.tier.value,
        "unit": series.unit,
        "population": series.population,
        "values": {
            str(year): value for year, value in sorted(series.values.items())
        },
        "values_minor": {
            str(year): value for year, value in sorted(series.values_minor.items())
        },
        "currency": series.currency,
        "notes": series.notes,
        "splices_from": series.splices_from,
        "measure": series.measure.value if series.measure is not None else None,
    }


def _fact_payload(fact: Fact) -> dict[str, object]:
    """Serialize one authored fact, retaining optional fields as ``null``."""
    return {
        "id": fact.id,
        "panel": fact.panel.value,
        "label": fact.label,
        "value": fact.value,
        "unit": fact.unit,
        "source": fact.source,
        "tier": fact.tier.value,
        "notes": fact.notes,
        "assumptions": list(fact.assumptions),
        "amount_minor": fact.amount_minor,
        "currency": fact.currency,
        "price_year": fact.price_year,
        "basis": fact.basis.value if fact.basis is not None else None,
        "quantity": fact.quantity,
    }


def _inflation_payload(
    derived: DerivedFact, series: Mapping[str, Series]
) -> dict[str, object] | None:
    """Return the exact series observations used by an inflation derivation."""
    if derived.op is not DerivedOp.INFLATE:
        return None
    source_series = series.get(derived.inflate_series)
    if source_series is None:
        raise ValueError(
            f"derived {derived.id!r}: inflation series {derived.inflate_series!r} "
            "is required in the export"
        )
    values: Mapping[int, float | int]
    values = source_series.values_minor if source_series.values_minor else source_series.values
    try:
        from_value = values[derived.inflate_from_year]
        to_value = values[derived.inflate_to_year]
    except KeyError as exc:
        raise ValueError(
            f"derived {derived.id!r}: inflation series observation is missing"
        ) from exc
    return {
        "series_id": source_series.id,
        "from": {"year": derived.inflate_from_year, "value": from_value},
        "to": {"year": derived.inflate_to_year, "value": to_value},
    }


def _derived_payload(
    derived: DerivedFact,
    computed: ComputedFact,
    series: Mapping[str, Series],
) -> dict[str, object]:
    """Serialize authored derivation structure plus its build-time result."""
    return {
        "id": derived.id,
        "panel": derived.panel.value,
        "label": derived.label,
        "unit": derived.unit,
        "op": derived.op.value,
        "numerator": derived.numerator,
        "denominator": derived.denominator,
        "precision": derived.precision,
        "notes": derived.notes,
        "assumptions": list(derived.assumptions),
        "inflate_series": derived.inflate_series,
        "inflate_from_year": derived.inflate_from_year,
        "inflate_to_year": derived.inflate_to_year,
        "count_series": list(derived.count_series),
        "threshold": derived.threshold or None,
        "at_year": derived.at_year or None,
        "value": computed.value,
        "computed_value": computed.numeric_value,
        "computed_amount_minor": computed.amount_minor,
        "computed_currency": computed.currency or None,
        "tier": computed.tier.value,
        "inflation": _inflation_payload(derived, series),
    }


def _reject_nonfinite(value: object, path: str = "payload") -> None:
    """Reject NaN/Infinity before they can enter a machine-readable export."""
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path}: non-finite float is not exportable")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_nonfinite(item, f"{path}.{key}")
    elif isinstance(value, list | tuple):
        for index, item in enumerate(value):
            _reject_nonfinite(item, f"{path}[{index}]")


def _computed_by_room(
    corpus: Corpus, series: Mapping[str, Series]
) -> dict[str, tuple[ComputedFact, ...]]:
    """Evaluate all room derivations using the same index as the site build."""
    fact_index = {
        fact.id: fact for room in corpus.rooms for fact in room.facts
    }
    return {
        room.slug: evaluate_room(room, dict(series), fact_index)
        for room in corpus.rooms
    }


def _room_payload(
    room: Room, computed: tuple[ComputedFact, ...], series: Mapping[str, Series]
) -> dict[str, object]:
    computed_by_id = {fact.id: fact for fact in computed}
    return {
        "country": room.country,
        "decade": room.decade,
        "slug": room.slug,
        "wage_anchor": room.wage_anchor,
        "income_anchor": room.income_anchor,
        "data_as_of": room.data_as_of,
        "facts": [
            _fact_payload(fact) for fact in sorted(room.facts, key=lambda fact: fact.id)
        ],
        "derived": [
            _derived_payload(derived, computed_by_id[derived.id], series)
            for derived in sorted(room.derived, key=lambda item: item.id)
        ],
    }


def corpus_payload(
    corpus: Corpus,
    series: Mapping[str, Series] | None = None,
    computed_by_room: Mapping[str, tuple[ComputedFact, ...]] | None = None,
) -> dict[str, object]:
    """Return the canonical, JSON-compatible corpus export payload.

    ``computed_by_room`` is accepted by the site build so derived facts are
    evaluated once and shared with the rendered pages.  The standalone API
    evaluates them here from the supplied series.
    """
    series_by_id = {} if series is None else dict(series)
    if computed_by_room is None:
        computed_by_room = _computed_by_room(corpus, series_by_id)

    rooms = sorted(corpus.rooms, key=lambda room: (room.country, room.decade))
    return {
        "schema_version": SCHEMA_VERSION,
        "rooms": [
            _room_payload(room, computed_by_room.get(room.slug, ()), series_by_id)
            for room in rooms
        ],
        "sources": [
            _source_payload(corpus.sources[source_id])
            for source_id in sorted(corpus.sources)
        ],
        "assumptions": [
            _assumption_payload(corpus.assumptions[assumption_id])
            for assumption_id in sorted(corpus.assumptions)
        ],
        "series": [
            _series_payload(series_by_id[series_id]) for series_id in sorted(series_by_id)
        ],
    }


def _quantified_rows(corpus: Corpus) -> list[dict[str, object]]:
    """Build the canonical row set for ``facts.csv``."""
    rows: list[dict[str, object]] = []
    rooms = sorted(corpus.rooms, key=lambda room: (room.country, room.decade))
    for room in rooms:
        for fact in sorted(room.facts, key=lambda item: item.id):
            if fact.quantity is None:
                continue
            source = corpus.sources[fact.source]
            rows.append(
                {
                    "id": fact.id,
                    "decade": room.decade,
                    "panel": fact.panel.value,
                    "label": fact.label,
                    "value": fact.value,
                    "quantity": fact.quantity,
                    "unit": fact.unit,
                    "tier": fact.tier.value,
                    "source_id": fact.source,
                    "short_cite": source.short_cite,
                }
            )
    return rows


def quantified_fact_count(corpus: Corpus) -> int:
    """Return the number of authored facts represented in the CSV export."""
    return sum(1 for room in corpus.rooms for fact in room.facts if fact.quantity is not None)


def _csv_text(corpus: Corpus) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(_quantified_rows(corpus))
    return output.getvalue()


def _spreadsheet_safe(value: object) -> object:
    """Prefix formula-like text without changing the canonical CSV/JSON data."""
    if isinstance(value, str) and value.lstrip(" \t\r\n").startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def _safe_csv_text(corpus: Corpus) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    safe_rows = [
        {field: _spreadsheet_safe(value) for field, value in row.items()}
        for row in _quantified_rows(corpus)
    ]
    writer.writerows(safe_rows)
    return output.getvalue()


def export_corpus(
    corpus: Corpus,
    out_dir: Path,
    series: Mapping[str, Series] | None = None,
    computed_by_room: Mapping[str, tuple[ComputedFact, ...]] | None = None,
    *,
    source_dir: Path | None = None,
    lock_root: Path | None = None,
) -> None:
    """Write deterministic JSON and CSV exports below ``out_dir/data``.

    ``source_dir`` is supplied by the CLI/build path so an output cannot be
    the corpus itself, a descendant of it, or a directory containing it.
    ``lock_root`` is the logical output root used to coordinate a nested data
    surface with a full-site publication; direct callers default to ``out_dir``.
    """
    payload = corpus_payload(corpus, series, computed_by_room)
    _reject_nonfinite(payload)
    validate_destination(
        out_dir,
        forbidden_paths=(source_dir,) if source_dir is not None else (),
    )
    publication_root = lock_root if lock_root is not None else out_dir
    with staged_directory(
        out_dir / "data",
        lock_root=publication_root,
        cleanup_roots=(publication_root, publication_root / "data"),
    ) as data_dir:
        try:
            ensure_publishable_directory(out_dir)
        except OSError as exc:
            raise OutputError(
                f"could not prepare export output directory: {out_dir}"
            ) from exc
        with (data_dir / "corpus.json").open("w", encoding="utf-8", newline="\n") as handle:
            # Payload builders sort every collection; insertion order keeps
            # year observations chronological without lexicographic key sorting.
            handle.write(
                json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
            )
            handle.write("\n")
        with (data_dir / RAW_CSV_FILENAME).open(
            "w", encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(_csv_text(corpus))
        with (data_dir / SAFE_CSV_FILENAME).open(
            "w", encoding="utf-8-sig", newline="\n"
        ) as handle:
            handle.write(_safe_csv_text(corpus))


__all__ = [
    "CSV_FIELDS",
    "RAW_CSV_FILENAME",
    "SAFE_CSV_FILENAME",
    "SCHEMA_VERSION",
    "corpus_payload",
    "export_corpus",
    "quantified_fact_count",
]
