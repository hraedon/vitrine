"""The series layer — annual time series that feed charts (plan 010).

A series is a named year→value table with one source, one tier, one
population. Unlike a :class:`~vitrine.model.Fact` it carries no ``panel`` and
never renders in a room; it exists so corridor and affordability charts can
draw from the full annual record (50–112 points) instead of one curated
representative year per decade. The decade facts remain the room's voice; the
series is the chart's voice.

Stdlib only (``tomllib``, ``dataclasses``), like the rest of the core. The
architecture test holds: this module must not import anything from ``site/``.
"""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from vitrine.model import Measure, Tier


class SeriesError(Exception):
    """A series data file is structurally malformed."""


@dataclass(frozen=True, slots=True)
class Series:
    """One named time series with uniform provenance — plan 010.

    Exactly one of ``values`` (floats: CPI, hours, percentages) or
    ``values_minor`` (integer minor units / cents: monetary series) is set.
    The no-float-drift convention from the fact model applies: monetary series
    live in integer cents.
    """

    id: str
    label: str
    source: str  # Source.id, resolved by the gate
    tier: Tier
    unit: str
    population: str
    values: dict[int, float] = field(default_factory=dict)
    values_minor: dict[int, int] = field(default_factory=dict)
    notes: str = ""
    splices_from: str = ""  # optional: another series id + splice note
    measure: Measure | None = None  # set iff the series is an affordability axis


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise SeriesError(f"{path}: invalid TOML: {exc}") from exc


def _require_str(table: Mapping[str, Any], key: str, ctx: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SeriesError(f"{ctx}: field {key!r} missing or not a non-empty string")
    return value


def _opt_str(table: Mapping[str, Any], key: str, ctx: str) -> str:
    value = table.get(key, "")
    if not isinstance(value, str):
        raise SeriesError(f"{ctx}: field {key!r} must be a string")
    return value


def _parse_measure(table: Mapping[str, Any], ctx: str) -> Measure | None:
    if "measure" not in table:
        return None
    raw = table["measure"]
    if not isinstance(raw, str):
        raise SeriesError(f"{ctx}: field 'measure' must be a string")
    allowed = {m.value: m for m in Measure}
    if raw not in allowed:
        raise SeriesError(
            f"{ctx}: measure {raw!r} not one of: {', '.join(sorted(allowed))}"
        )
    return allowed[raw]


def _parse_value_table(
    table: Mapping[str, Any], key: str, ctx: str
) -> dict[int, float]:
    """Parse a year→float mapping; year keys must parse to int."""
    raw = table.get(key)
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise SeriesError(f"{ctx}: field {key!r} must be a TOML table")
    out: dict[int, float] = {}
    for year_key, val in raw.items():
        try:
            year = int(year_key)
        except (TypeError, ValueError) as exc:
            raise SeriesError(
                f"{ctx}: {key!r} key {year_key!r} is not an integer year"
            ) from exc
        if isinstance(val, bool) or not isinstance(val, int | float):
            raise SeriesError(
                f"{ctx}: {key!r}[{year}] must be a number, got {type(val).__name__}"
            )
        out[year] = float(val)
    return out


def _parse_minor_table(
    table: Mapping[str, Any], key: str, ctx: str
) -> dict[int, int]:
    """Parse a year→int mapping; values must be integers (integer cents)."""
    raw = table.get(key)
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise SeriesError(f"{ctx}: field {key!r} must be a TOML table")
    out: dict[int, int] = {}
    for year_key, val in raw.items():
        try:
            year = int(year_key)
        except (TypeError, ValueError) as exc:
            raise SeriesError(
                f"{ctx}: {key!r} key {year_key!r} is not an integer year"
            ) from exc
        if isinstance(val, bool) or not isinstance(val, int):
            raise SeriesError(
                f"{ctx}: {key!r}[{year}] must be an integer, got {type(val).__name__}"
            )
        out[year] = int(val)
    return out


def _load_series_file(path: Path) -> list[Series]:
    data = _read_toml(path)
    raw_series = data.get("series", [])
    if isinstance(raw_series, Mapping):
        raise SeriesError(
            f"{path}: 'series' must be an array of tables ([[series]]), "
            f"not a single table ([series])"
        )
    if not isinstance(raw_series, list):
        raise SeriesError(f"{path}: 'series' must be an array of tables")
    series_list: list[Series] = []
    for entry in raw_series:
        ctx = f"{path} [[series]]"
        sid = _require_str(entry, "id", ctx)
        ctx = f"{path} series {sid!r}"
        raw_tier = _require_str(entry, "tier", ctx)
        allowed_tiers = {t.value: t for t in Tier}
        if raw_tier not in allowed_tiers:
            raise SeriesError(
                f"{ctx}: tier {raw_tier!r} not one of: {', '.join(sorted(allowed_tiers))}"
            )
        series_list.append(
            Series(
                id=sid,
                label=_require_str(entry, "label", ctx),
                source=_require_str(entry, "source", ctx),
                tier=allowed_tiers[raw_tier],
                unit=_require_str(entry, "unit", ctx),
                population=_require_str(entry, "population", ctx),
                values=_parse_value_table(entry, "values", ctx),
                values_minor=_parse_minor_table(entry, "values_minor", ctx),
                notes=_opt_str(entry, "notes", ctx),
                splices_from=_opt_str(entry, "splices_from", ctx),
                measure=_parse_measure(entry, ctx),
            )
        )
    return series_list


def load_series(data_dir: Path) -> dict[str, Series]:
    """Load every ``data/series/*.toml`` file into a single id→Series map.

    Returns an empty dict if no series directory exists (the layer is optional
    until a chart references one). Duplicate ids across files are an error.
    """
    series_dir = data_dir / "series"
    if not series_dir.is_dir():
        return {}
    out: dict[str, Series] = {}
    for path in sorted(series_dir.glob("*.toml")):
        for series in _load_series_file(path):
            if series.id in out:
                raise SeriesError(
                    f"{path}: duplicate series id {series.id!r} "
                    f"(also defined in data/series/)"
                )
            out[series.id] = series
    return out
