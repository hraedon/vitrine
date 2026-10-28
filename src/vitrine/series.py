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

import math
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, assert_never

from vitrine import money
from vitrine.model import Basis, Measure, SeriesKind, Tier


class SeriesError(Exception):
    """A series data file is structurally malformed."""


@dataclass(frozen=True, slots=True)
class Series:
    """One named time series with uniform provenance — plan 010.

    Exactly one of ``values`` or ``values_minor`` is set. Ordinary quantities
    use ``values`` without currency. Monetary amounts use integer minor units.
    Monetary rates use ``values`` in major units with currency and an explicit
    ``rate_basis``, preserving subcent annual means without rounding to cents.
    """

    id: str
    label: str
    source: str  # Source.id, resolved by the gate
    tier: Tier
    unit: str
    population: str
    values: dict[int, float] = field(default_factory=dict)
    values_minor: dict[int, int] = field(default_factory=dict)
    currency: str = ""  # required for monetary amounts and rates; forbidden for quantities
    notes: str = ""
    splices_from: str = ""  # optional: another series id + splice note
    measure: Measure | None = None  # set iff the series is an affordability axis
    rate_basis: Basis | None = None  # rates only; TOTAL is invalid

    @property
    def kind(self) -> SeriesKind:
        """Resolve representation from the numeric storage and rate metadata.

        The gate rejects empty/mixed tables and rate metadata on minor-unit
        amounts before consumers use this classification.
        """
        if self.values_minor:
            return SeriesKind.MONETARY_AMOUNT
        if self.rate_basis is not None:
            return SeriesKind.MONETARY_RATE
        return SeriesKind.QUANTITY

    @property
    def monetary(self) -> bool:
        match self.kind:
            case SeriesKind.QUANTITY:
                return False
            case SeriesKind.MONETARY_AMOUNT | SeriesKind.MONETARY_RATE:
                return True
            case _ as unreachable:
                assert_never(unreachable)


def representation_problems(series: Series) -> list[str]:
    """Validate storage/currency semantics for loaded and programmatic series."""
    problems: list[str] = []
    if not series.values and not series.values_minor:
        problems.append("has neither 'values' nor 'values_minor'")
    if series.values and series.values_minor:
        problems.append("has both 'values' and 'values_minor' — declare exactly one")
    for year, value in series.values.items():
        if isinstance(value, bool) or not math.isfinite(value):
            problems.append(f"values[{year}] is not a finite number")
    for year, minor in series.values_minor.items():
        if isinstance(minor, bool) or not isinstance(minor, int):
            problems.append(f"values_minor[{year}] must be an integer, not a boolean or float")
    if series.rate_basis is Basis.TOTAL:
        problems.append("monetary_rate rate_basis must be hourly, weekly, monthly or annual")
    if series.rate_basis is not None and series.values_minor:
        problems.append("monetary_rate must use values in major units, not values_minor")
    match series.kind:
        case SeriesKind.QUANTITY:
            if series.currency:
                problems.append("currency set on a non-monetary quantity series")
        case SeriesKind.MONETARY_AMOUNT | SeriesKind.MONETARY_RATE:
            if not series.currency:
                problems.append(f"{series.kind.value} series must declare currency")
            elif not money.is_known(series.currency):
                problems.append(f"unknown currency {series.currency!r} — register it in money")
        case _ as unreachable:
            assert_never(unreachable)
    return problems


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
        if year in out:
            raise SeriesError(f"{ctx}: duplicate numeric year {year} in {key!r}")
        if isinstance(val, bool) or not isinstance(val, int | float):
            raise SeriesError(
                f"{ctx}: {key!r}[{year}] must be a number, got {type(val).__name__}"
            )
        numeric = float(val)
        if not math.isfinite(numeric):
            raise SeriesError(f"{ctx}: {key!r}[{year}] must be a finite number")
        out[year] = numeric
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
        if year in out:
            raise SeriesError(f"{ctx}: duplicate numeric year {year} in {key!r}")
        if isinstance(val, bool) or not isinstance(val, int):
            raise SeriesError(
                f"{ctx}: {key!r}[{year}] must be an integer, got {type(val).__name__}"
            )
        out[year] = int(val)
    return out


def _parse_rate_basis(table: Mapping[str, Any], ctx: str, has_minor: bool) -> Basis | None:
    """Legacy storage infers quantities/amounts; rates require explicit tagging."""
    inferred = SeriesKind.MONETARY_AMOUNT if has_minor else SeriesKind.QUANTITY
    raw_kind = table.get("kind", inferred.value)
    try:
        kind = SeriesKind(raw_kind)
    except (TypeError, ValueError) as exc:
        raise SeriesError(f"{ctx}: unknown series kind {raw_kind!r}") from exc
    raw_basis = table.get("rate_basis")
    match kind:
        case SeriesKind.MONETARY_RATE:
            if has_minor:
                raise SeriesError(f"{ctx}: monetary_rate must use values, not values_minor")
            try:
                basis = Basis(raw_basis)
            except (TypeError, ValueError) as exc:
                raise SeriesError(f"{ctx}: monetary_rate requires a valid rate_basis") from exc
            if basis is Basis.TOTAL:
                raise SeriesError(f"{ctx}: monetary_rate rate_basis cannot be total")
            return basis
        case SeriesKind.QUANTITY | SeriesKind.MONETARY_AMOUNT:
            if raw_basis is not None:
                raise SeriesError(f"{ctx}: rate_basis requires kind = 'monetary_rate'")
            if kind is not inferred:
                raise SeriesError(f"{ctx}: kind {kind.value!r} disagrees with observation storage")
            return None
        case _ as unreachable:
            assert_never(unreachable)


def _parse_currency(
    table: Mapping[str, Any], ctx: str, has_minor: bool, rate_basis: Basis | None,
) -> str:
    """Currency is mandatory on monetary amounts/rates and absent on quantities."""
    raw = table.get("currency", "")
    if not isinstance(raw, str):
        raise SeriesError(f"{ctx}: field 'currency' must be a string")
    monetary = has_minor or rate_basis is not None
    if monetary and not raw.strip():
        raise SeriesError(
            f"{ctx}: monetary series must declare currency "
            f"(e.g. \"USD\") — the money registry scales and formats it"
        )
    if not monetary and raw.strip():
        raise SeriesError(
            f"{ctx}: currency {raw!r} set on a non-monetary series (values "
            f"only) — indexes and quantities are dimensionless; the museum "
            f"never converts between currencies"
        )
    return raw


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
        values = _parse_value_table(entry, "values", ctx)
        values_minor = _parse_minor_table(entry, "values_minor", ctx)
        rate_basis = _parse_rate_basis(entry, ctx, bool(values_minor))
        series_list.append(
            Series(
                id=sid,
                label=_require_str(entry, "label", ctx),
                source=_require_str(entry, "source", ctx),
                tier=allowed_tiers[raw_tier],
                unit=_require_str(entry, "unit", ctx),
                population=_require_str(entry, "population", ctx),
                values=values,
                values_minor=values_minor,
                currency=_parse_currency(entry, ctx, bool(values_minor), rate_basis),
                notes=_opt_str(entry, "notes", ctx),
                splices_from=_opt_str(entry, "splices_from", ctx),
                measure=_parse_measure(entry, ctx),
                rate_basis=rate_basis,
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
