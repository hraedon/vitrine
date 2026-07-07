"""Load data/ into the fact model. Stdlib only (tomllib).

Structural problems (missing fields, bad enum values, wrong types) are
rejected here with the file path in the message; referential problems
(dangling source ids, duplicates) are the checker's job.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from vitrine.model import (
    Assumption,
    Basis,
    Corpus,
    DerivedFact,
    DerivedOp,
    Fact,
    Measure,
    Panel,
    Room,
    Source,
    Tier,
)


class LoadError(Exception):
    """A data file is structurally malformed."""


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise LoadError(f"{path}: invalid TOML: {exc}") from exc


def _get_str(table: Mapping[str, Any], key: str, ctx: str) -> str:
    value = table.get(key)
    if not isinstance(value, str):
        raise LoadError(f"{ctx}: field {key!r} missing or not a string")
    return value


def _get_str_opt(table: Mapping[str, Any], key: str, ctx: str) -> str:
    value = table.get(key, "")
    if not isinstance(value, str):
        raise LoadError(f"{ctx}: field {key!r} must be a string")
    return value


def _get_int(table: Mapping[str, Any], key: str, ctx: str) -> int:
    value = table.get(key)
    if not isinstance(value, int):
        raise LoadError(f"{ctx}: field {key!r} missing or not an integer")
    return value


def _get_int_opt(table: Mapping[str, Any], key: str, ctx: str) -> int | None:
    if key not in table:
        return None
    value = table[key]
    if not isinstance(value, int):
        raise LoadError(f"{ctx}: field {key!r} must be an integer")
    return value


def _get_str_list(table: Mapping[str, Any], key: str, ctx: str) -> tuple[str, ...]:
    value = table.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise LoadError(f"{ctx}: field {key!r} must be a list of strings")
    return tuple(value)


def _load_sources(path: Path) -> dict[str, Source]:
    data = _read_toml(path)
    sources: dict[str, Source] = {}
    for table in data.get("source", []):
        ctx = f"{path} [[source]]"
        source = Source(
            id=_get_str(table, "id", ctx),
            title=_get_str(table, "title", ctx),
            publisher=_get_str(table, "publisher", ctx),
            year=_get_int(table, "year", ctx),
            url=_get_str(table, "url", ctx),
            population=_get_str(table, "population", ctx),
            notes=_get_str_opt(table, "notes", ctx),
            short_cite=_get_str_opt(table, "short_cite", ctx),
            measure=_parse_measure(table, ctx),
        )
        if source.id in sources:
            raise LoadError(f"{path}: duplicate source id {source.id!r}")
        sources[source.id] = source
    return sources


def _load_assumptions(path: Path) -> dict[str, Assumption]:
    data = _read_toml(path)
    assumptions: dict[str, Assumption] = {}
    for table in data.get("assumption", []):
        ctx = f"{path} [[assumption]]"
        assumption = Assumption(
            id=_get_str(table, "id", ctx),
            title=_get_str(table, "title", ctx),
            statement=_get_str(table, "statement", ctx),
        )
        if assumption.id in assumptions:
            raise LoadError(f"{path}: duplicate assumption id {assumption.id!r}")
        assumptions[assumption.id] = assumption
    return assumptions


def _parse_enum(raw: str, values: dict[str, Any], kind: str, ctx: str) -> Any:
    if raw not in values:
        allowed = ", ".join(sorted(values))
        raise LoadError(f"{ctx}: {kind} {raw!r} not one of: {allowed}")
    return values[raw]


def _parse_basis(table: Mapping[str, Any], ctx: str) -> Basis | None:
    if "basis" not in table:
        return None
    raw = table["basis"]
    if not isinstance(raw, str):
        raise LoadError(f"{ctx}: field 'basis' must be a string")
    basis: Basis = _parse_enum(raw, {b.value: b for b in Basis}, "basis", ctx)
    return basis


def _parse_measure(table: Mapping[str, Any], ctx: str) -> Measure | None:
    if "measure" not in table:
        return None
    raw = table["measure"]
    if not isinstance(raw, str):
        raise LoadError(f"{ctx}: field 'measure' must be a string")
    measure: Measure = _parse_enum(raw, {m.value: m for m in Measure}, "measure", ctx)
    return measure


def _load_room(path: Path) -> Room:
    data = _read_toml(path)
    meta = data.get("room")
    if not isinstance(meta, dict):
        raise LoadError(f"{path}: missing [room] table")
    country = _get_str(meta, "country", f"{path} [room]")
    decade = _get_str(meta, "decade", f"{path} [room]")

    facts: list[Fact] = []
    for table in data.get("fact", []):
        ctx = f"{path} [[fact]]"
        fact_id = _get_str(table, "id", ctx)
        ctx = f"{path} fact {fact_id!r}"
        panel: Panel = _parse_enum(
            _get_str(table, "panel", ctx), {p.value: p for p in Panel}, "panel", ctx
        )
        tier: Tier = _parse_enum(
            _get_str(table, "tier", ctx), {t.value: t for t in Tier}, "tier", ctx
        )
        facts.append(
            Fact(
                id=fact_id,
                panel=panel,
                label=_get_str(table, "label", ctx),
                value=_get_str(table, "value", ctx),
                unit=_get_str(table, "unit", ctx),
                source=_get_str(table, "source", ctx),
                tier=tier,
                notes=_get_str_opt(table, "notes", ctx),
                assumptions=_get_str_list(table, "assumptions", ctx),
                amount_minor=_get_int_opt(table, "amount_minor", ctx),
                currency=_get_str_opt(table, "currency", ctx),
                price_year=_get_int_opt(table, "price_year", ctx),
                basis=_parse_basis(table, ctx),
            )
        )
    derived: list[DerivedFact] = []
    for table in data.get("derived", []):
        ctx = f"{path} [[derived]]"
        derived_id = _get_str(table, "id", ctx)
        ctx = f"{path} derived {derived_id!r}"
        derived_panel: Panel = _parse_enum(
            _get_str(table, "panel", ctx), {p.value: p for p in Panel}, "panel", ctx
        )
        op: DerivedOp = _parse_enum(
            _get_str(table, "op", ctx), {o.value: o for o in DerivedOp}, "op", ctx
        )
        precision = _get_int_opt(table, "precision", ctx)
        if precision is not None and not 0 <= precision <= 4:
            raise LoadError(f"{ctx}: precision must be between 0 and 4")
        derived.append(
            DerivedFact(
                id=derived_id,
                panel=derived_panel,
                label=_get_str(table, "label", ctx),
                unit=_get_str(table, "unit", ctx),
                op=op,
                numerator=_get_str(table, "numerator", ctx),
                denominator=_get_str(table, "denominator", ctx),
                precision=precision if precision is not None else 1,
                notes=_get_str_opt(table, "notes", ctx),
                assumptions=_get_str_list(table, "assumptions", ctx),
            )
        )
    return Room(
        country=country,
        decade=decade,
        facts=tuple(facts),
        derived=tuple(derived),
        wage_anchor=_get_str_opt(meta, "wage_anchor", f"{path} [room]"),
        income_anchor=_get_str_opt(meta, "income_anchor", f"{path} [room]"),
    )


def load_corpus(data_dir: Path) -> Corpus:
    """Load the whole museum from a data directory."""
    sources_path = data_dir / "sources.toml"
    assumptions_path = data_dir / "assumptions.toml"
    if not sources_path.is_file():
        raise LoadError(f"{sources_path}: missing source registry")
    if not assumptions_path.is_file():
        raise LoadError(f"{assumptions_path}: missing assumption ledger")

    rooms = tuple(
        _load_room(path)
        for path in sorted(data_dir.glob("*/*.toml"))
    )
    return Corpus(
        sources=_load_sources(sources_path),
        assumptions=_load_assumptions(assumptions_path),
        rooms=rooms,
    )
