"""Offline transcription checks and a content-bound audit ledger (Plan 015).

The ledger pins the exact sample bytes, not the identity or authority of a
publisher. A successful extraction checks transcription, not interpretation.
Only this module optionally imports openpyxl; the gate remains stdlib-only.
"""

from __future__ import annotations

import csv
import enum
import hashlib
import io
import json
import os
import re
import tempfile
import tomllib
from contextlib import suppress
from dataclasses import asdict
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import assert_never
from xml.etree.ElementTree import ParseError
from zipfile import BadZipFile

from vitrine.model import (
    AuditCalculation,
    AuditEntry,
    AuditGuard,
    AuditOperation,
    AuditRef,
    AuditRounding,
    AuditTarget,
    Corpus,
    Extractor,
    Fact,
    Tier,
)

LEDGER_VERSION = 2


def decimal_value(value: object) -> Decimal:
    """Parse a single source numeral; reject annotations, blanks and nonfinite values."""
    if isinstance(value, bool) or value is None:
        raise ValueError("not a number")
    text = str(value).strip()
    if not re.fullmatch(r"[$£¥]?\s*[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*%?", text):
        raise ValueError(f"not a single unannotated numeral: {text!r}")
    return Decimal(re.sub(r"[$£¥,%\s]", "", text))


def _scale(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("audit scale must be a finite positive decimal") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError("audit scale must be a finite positive decimal")
    return result


def _validate_locator(extractor: Extractor, locator: str) -> None:
    match extractor:
        case Extractor.CSV_CELL:
            valid = re.fullmatch(r"R[1-9]\d*:C[1-9]\d*", locator) is not None
        case Extractor.XLSX_CELL:
            valid = re.fullmatch(r"[^!]+![A-Z]+[1-9]\d*", locator) is not None
        case Extractor.TEXT_REGEX:
            try:
                valid = re.compile(locator).groups == 1
            except re.error as exc:
                raise ValueError(f"invalid audit regex: {exc}") from exc
        case Extractor.JSON_POINTER:
            valid = locator.startswith("/") and re.search(r"~(?![01])", locator) is None
        case _:
            assert_never(extractor)
    if not valid:
        raise ValueError(f"invalid {extractor.value} locator: {locator!r}")


def validate_ref(ref: AuditRef) -> None:
    if ref.encoding not in {"utf-8-sig", "utf-8", "cp932"}:
        raise ValueError("audit encoding must be utf-8-sig, utf-8, or cp932")
    path = PurePosixPath(ref.file)
    if (
        not ref.file
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in ref.file
        or ":" in ref.file
        or str(path) != ref.file
        or any(ord(c) < 32 for c in ref.file)
    ):
        raise ValueError("audit file must be a normalized relative samples path")
    _scale(ref.scale)
    _validate_locator(ref.extractor, ref.locator)
    for guard in ref.guards:
        _validate_locator(ref.extractor, guard.locator)
        if not guard.value:
            raise ValueError("audit guard needs an expected source heading or year")
    calc = ref.calculation
    if calc is not None:
        if type(calc.precision) is not int or not 0 <= calc.precision <= 8:
            raise ValueError("audit calculation precision must be an integer from 0 to 8")
        if not calc.method.strip():
            raise ValueError("audit calculation needs a documented method")
        locators = (ref.locator, *calc.operands)
        if len(set(locators)) != len(locators):
            raise ValueError("audit calculation operands must have distinct addresses")
        match calc.op:
            case AuditOperation.MEAN:
                if len(locators) < 2:
                    raise ValueError("mean needs at least two source operands")
            case AuditOperation.PCT_OF:
                if len(locators) != 2:
                    raise ValueError("pct_of needs a numerator and denominator")
            case _:
                assert_never(calc.op)
        for locator in calc.operands:
            _validate_locator(ref.extractor, locator)


def _parse_calculation(raw: object) -> AuditCalculation:
    fields = {"op", "operands", "precision", "rounding", "method"}
    if not isinstance(raw, dict) or set(raw) != fields:
        raise ValueError("audit calculation requires op, operands, precision, rounding and method")
    if not isinstance(raw["operands"], list) or not all(
        isinstance(item, str) for item in raw["operands"]
    ):
        raise ValueError("audit calculation operands must be source addresses")
    if not isinstance(raw["method"], str) or type(raw["precision"]) is not int:
        raise ValueError("audit calculation needs a string method and integer precision")
    return AuditCalculation(
        AuditOperation(raw["op"]), tuple(raw["operands"]), raw["precision"],
        AuditRounding(raw["rounding"]), raw["method"],
    )


def parse_ref(table: object) -> AuditRef:
    if not isinstance(table, dict):
        raise ValueError("audit must be a table")
    if set(table) - {
        "file", "extractor", "locator", "scale", "target", "guards", "encoding", "calculation",
    }:
        raise ValueError("unknown audit field")
    for key in ("file", "extractor", "locator"):
        if not isinstance(table.get(key), str):
            raise ValueError(f"audit {key} must be a string")
    raw_scale = table.get("scale", "1")
    if isinstance(raw_scale, bool) or not isinstance(raw_scale, str | int | float):
        raise ValueError("audit scale must be a decimal")
    guards = table.get("guards", [])
    if not isinstance(guards, list):
        raise ValueError("audit guards must be an array")
    for guard in guards:
        if (
            not isinstance(guard, dict)
            or set(guard) != {"locator", "value"}
            or not all(isinstance(v, str) for v in guard.values())
        ):
            raise ValueError("audit guard needs string locator and value")
    ref = AuditRef(
        file=table["file"],
        extractor=Extractor(table["extractor"]),
        locator=table["locator"],
        scale=str(raw_scale),
        target=AuditTarget(table.get("target", "quantity")),
        guards=tuple(AuditGuard(**guard) for guard in guards),
        encoding=str(table.get("encoding", "utf-8-sig")),
        calculation=_parse_calculation(table["calculation"]) if "calculation" in table else None,
    )
    validate_ref(ref)
    return ref


def load_ledger(path: Path) -> tuple[AuditEntry, ...]:
    if not path.exists():
        return ()
    with path.open("rb") as stream:
        raw = tomllib.load(stream)
    if type(raw.get("version")) is not int or raw["version"] not in {1, LEDGER_VERSION}:
        raise ValueError("unsupported audit ledger version")
    entries = raw.get("entry", [])
    if not isinstance(entries, list) or set(raw) - {"version", "entry"}:
        raise ValueError("invalid audit ledger structure")
    result: list[AuditEntry] = []
    fields = {"fact_id", "fingerprint", "sample_sha256", "file", "extracted", "audited"}
    for entry in entries:
        if (
            not isinstance(entry, dict)
            or set(entry) - fields - {"operands"}
            or not fields <= set(entry)
            or not all(isinstance(entry[k], str) and entry[k] for k in fields)
        ):
            raise ValueError("invalid audit ledger entry")
        for key in ("fingerprint", "sample_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", entry[key]):
                raise ValueError(f"invalid audit ledger {key}")
        date.fromisoformat(entry["audited"])
        decimal_value(entry["extracted"])
        operands = entry.get("operands", [])
        if not isinstance(operands, list) or not all(isinstance(v, str) for v in operands):
            raise ValueError("invalid audit ledger operands")
        for value in operands:
            decimal_value(value)
        result.append(AuditEntry(**{k: entry[k] for k in fields}, operands=tuple(operands)))
    if len({e.fact_id for e in result}) != len(result):
        raise ValueError("duplicate audit ledger fact_id")
    return tuple(result)


def _json_default(value: object) -> str:
    if isinstance(value, enum.Enum):
        return str(value.value)
    raise TypeError(type(value).__name__)


def fingerprint(corpus: Corpus, fact: Fact) -> str:
    """Bind meaning as well as value; a different label or population invalidates the audit."""
    payload = {
        "version": LEDGER_VERSION,
        "fact": asdict(fact),
        "source": asdict(corpus.sources[fact.source]),
        "assumptions": [asdict(corpus.assumptions[a]) for a in fact.assumptions],
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=_json_default,
        allow_nan=False,
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def target_value(fact: Fact) -> Decimal:
    assert fact.audit is not None
    match fact.audit.target:
        case AuditTarget.QUANTITY:
            value = fact.quantity
        case AuditTarget.AMOUNT_MINOR:
            value = fact.amount_minor
        case _:
            assert_never(fact.audit.target)
    if value is None:
        raise ValueError(f"audit target {fact.audit.target.value} is missing")
    return decimal_value(value)


def calculate(ref: AuditRef, values: tuple[Decimal, ...]) -> Decimal:
    """Replay raw operands with exact rational arithmetic; round once, before unit scaling."""
    calc = ref.calculation
    if calc is None:
        if len(values) != 1:
            raise ValueError("literal audit needs exactly one source value")
        return values[0]
    if len(values) != 1 + len(calc.operands):
        raise ValueError("audit calculation operand count changed")
    operands = tuple(Fraction(value) for value in values)
    match calc.op:
        case AuditOperation.MEAN:
            result = sum(operands, Fraction()) / len(operands)
        case AuditOperation.PCT_OF:
            if operands[1] <= 0:
                raise ValueError("pct_of denominator must be positive")
            result = operands[0] * 100 / operands[1]
        case _:
            assert_never(calc.op)
    scaled = result * 10 ** calc.precision
    whole, remainder = divmod(abs(scaled.numerator), scaled.denominator)
    match calc.rounding:
        case AuditRounding.HALF_EVEN:
            round_tie = whole % 2 == 1
        case AuditRounding.HALF_UP:
            round_tie = True
        case _:
            assert_never(calc.rounding)
    if remainder * 2 > scaled.denominator or (
        remainder * 2 == scaled.denominator and round_tie
    ):
        whole += 1
    with localcontext() as context:
        context.prec = max(28, len(str(whole)) + calc.precision + 1)
        return Decimal(-whole if result < 0 else whole).scaleb(-calc.precision)


def _check_binding(corpus: Corpus, fact: Fact, entry: AuditEntry) -> None:
    ref = fact.audit
    if ref is None:
        raise ValueError("audit locator no longer exists")
    if fingerprint(corpus, fact) != entry.fingerprint:
        raise ValueError("stale fingerprint; re-audit")
    validate_ref(ref)
    extracted = decimal_value(entry.extracted)
    if ref.calculation is not None:
        replayed = calculate(ref, tuple(decimal_value(v) for v in entry.operands))
        if replayed != extracted:
            raise ValueError("ledger calculation does not reproduce extracted result")
    elif entry.operands:
        raise ValueError("literal audit cannot carry calculation operands")
    if (
        ref.file != entry.file
        or extracted * _scale(ref.scale) != target_value(fact)
    ):
        raise ValueError("stale fingerprint or extraction; re-audit")


def check_audits(corpus: Corpus) -> list[str]:
    """No archive or optional dependency needed: detect edits since a successful audit."""
    problems: list[str] = []
    facts = {f.id: f for r in corpus.rooms for f in r.facts}
    recorded = {entry.fact_id for entry in corpus.audit_ledger}
    for candidate in facts.values():
        if candidate.audit is not None:
            if candidate.id not in recorded:
                problems.append(f"audit {candidate.id}: no ledger entry; run vitrine audit")
            try:
                validate_ref(candidate.audit)
                target_value(candidate)
            except ValueError as exc:
                problems.append(f"fact {candidate.id}: {exc}")
    pins: dict[str, str] = {}
    for entry in corpus.audit_ledger:
        fact = facts.get(entry.fact_id)
        if fact is None or fact.audit is None:
            problems.append(f"audit {entry.fact_id}: fact or audit locator no longer exists")
            continue
        try:
            _check_binding(corpus, fact, entry)
        except (KeyError, ValueError) as exc:
            problems.append(f"audit {entry.fact_id}: invalid binding: {exc}")
        if entry.file in pins and pins[entry.file] != entry.sample_sha256:
            problems.append(f"audit {entry.fact_id}: inconsistent sample pin for {entry.file}")
        pins[entry.file] = entry.sample_sha256
    return problems


def _extract(blob: bytes, ref: AuditRef) -> tuple[tuple[object, ...], tuple[object, ...]]:
    operands = ref.calculation.operands if ref.calculation else ()
    locators = (ref.locator, *operands, *(g.locator for g in ref.guards))
    values: list[object] = []
    match ref.extractor:
        case Extractor.CSV_CELL:
            rows = list(csv.reader(io.StringIO(blob.decode(ref.encoding))))
            for locator in locators:
                row, col = (int(n) for n in re.findall(r"\d+", locator))
                values.append(rows[row - 1][col - 1])
        case Extractor.XLSX_CELL:
            try:
                import openpyxl  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ValueError("xlsx-cell requires the [audit] extra") from exc
            # Never accept a formula's possibly stale cached value as a transcription.
            book = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=False)
            try:
                for locator in locators:
                    sheet, cell = locator.rsplit("!", 1)
                    value = book[sheet][cell]
                    if value.data_type == "f":
                        raise ValueError(f"formula cell is not a literal source datum: {locator}")
                    values.append(value.value)
            finally:
                book.close()
        case Extractor.TEXT_REGEX:
            text = blob.decode(ref.encoding).replace("\r\n", "\n").replace("\r", "\n")
            for locator in locators:
                matches = list(re.finditer(locator, text, re.MULTILINE))
                if len(matches) != 1:
                    raise ValueError(f"regex must match exactly once; found {len(matches)}")
                values.append(matches[0].group(1))
        case Extractor.JSON_POINTER:
            document = json.loads(blob.decode(ref.encoding), parse_float=Decimal)
            for locator in locators:
                node = document
                for encoded in locator[1:].split("/"):
                    key = encoded.replace("~1", "/").replace("~0", "~")
                    if isinstance(node, list):
                        if re.fullmatch(r"0|[1-9]\d*", key) is None:
                            raise ValueError("JSON array address needs a canonical index")
                        node = node[int(key)]
                    elif isinstance(node, dict):
                        node = node[key]
                    else:
                        raise ValueError("JSON address traverses a scalar")
                if isinstance(node, dict | list) or node is None or isinstance(node, bool):
                    raise ValueError("JSON address must select a scalar source value")
                values.append(node)
        case _:
            assert_never(ref.extractor)
    count = 1 + len(operands)
    return tuple(values[:count]), tuple(values[count:])


def _sample(root: Path, relative: str) -> bytes:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("sample resolves outside the samples directory")
    return path.read_bytes()


def run_audit(
    corpus: Corpus,
    samples: Path,
    *,
    accept_changed_samples: bool = False,
    audited: str | None = None,
) -> tuple[tuple[AuditEntry, ...], list[str]]:
    """Read each source once, hash those same bytes, and return an all-or-nothing result."""
    entries: list[AuditEntry] = []
    problems: list[str] = []
    blobs: dict[str, bytes] = {}
    pins = {e.file: e.sample_sha256 for e in corpus.audit_ledger}
    for fact in sorted((f for r in corpus.rooms for f in r.facts if f.audit), key=lambda f: f.id):
        ref = fact.audit
        assert ref is not None
        try:
            validate_ref(ref)
            if ref.file not in blobs:
                blobs[ref.file] = _sample(samples, ref.file)
            blob = blobs[ref.file]
            digest = hashlib.sha256(blob).hexdigest()
            if ref.file in pins and digest != pins[ref.file] and not accept_changed_samples:
                raise ValueError("sample hash changed; inspect the archive before using --pin")
            values, guard_values = _extract(blob, ref)
            for guard, actual in zip(ref.guards, guard_values, strict=True):
                if str(actual).strip() != guard.value:
                    raise ValueError(f"source context changed at {guard.locator}: {actual!r}")
            numerals = tuple(decimal_value(value) for value in values)
            extracted = calculate(ref, numerals)
            if extracted * _scale(ref.scale) != target_value(fact):
                raise ValueError(
                    f"MISMATCH source {extracted} x {ref.scale} != {target_value(fact)}"
                )
            entries.append(
                AuditEntry(
                    fact_id=fact.id,
                    fingerprint=fingerprint(corpus, fact),
                    sample_sha256=digest,
                    file=ref.file,
                    extracted=format(extracted, "f"),
                    audited=audited or date.today().isoformat(),
                    operands=tuple(format(v, "f") for v in numerals) if ref.calculation else (),
                )
            )
        except FileNotFoundError:
            problems.append(f"{fact.id}: missing-file: {ref.file}")
        except (
            ValueError,
            OSError,
            IndexError,
            KeyError,
            csv.Error,
            BadZipFile,
            ParseError,
        ) as exc:
            problems.append(f"{fact.id}: parse-error: {exc}")
    # Never silently drop previously audited facts or locators.
    ids = {e.fact_id for e in entries}
    for old in corpus.audit_ledger:
        if old.fact_id not in ids and not any(p.startswith(old.fact_id + ":") for p in problems):
            problems.append(f"{old.fact_id}: audited fact or locator removed; review required")
    return (() if problems else tuple(entries)), problems


def write_ledger(path: Path, entries: tuple[AuditEntry, ...]) -> None:
    lines = [
        "# Generated by vitrine audit. Sample hashes are the archive pins.",
        f"version = {LEDGER_VERSION}",
        "",
    ]
    for entry in sorted(entries, key=lambda e: e.fact_id):
        lines.append("[[entry]]")
        for key, value in asdict(entry).items():
            lines.append(f"{key} = {json.dumps(value, ensure_ascii=True)}")
        lines.append("")
    # One atomic file replaces the draft's mutually dependent ledger + SHA256SUMS.
    fd, temporary = tempfile.mkstemp(prefix=".audit-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write("\n".join(lines))
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def coverage_report(corpus: Corpus) -> str:
    ledger = {entry.fact_id: entry for entry in corpus.audit_ledger}
    lines = [
        "Transcription audit coverage (current ledger bindings; archive not re-read)",
        "room / tier: facts | locators | current | unaudited-or-stale",
    ]
    totals = [0, 0, 0]
    for room in corpus.rooms:
        for tier in Tier:
            facts = [fact for fact in room.facts if fact.tier is tier]
            if not facts:
                continue
            locators = sum(fact.audit is not None for fact in facts)
            current = 0
            for fact in facts:
                entry = ledger.get(fact.id)
                if entry and fact.audit:
                    with suppress(KeyError, ValueError):
                        _check_binding(corpus, fact, entry)
                        current += 1
            lines.append(
                f"{room.slug} / {tier.value}: {len(facts)} | {locators} | "
                f"{current} | {len(facts) - current}"
            )
            for i, n in enumerate((len(facts), locators, current)):
                totals[i] += n
    lines.append(
        f"total: {totals[0]} facts | {totals[1]} locators | {totals[2]} current | "
        f"{totals[0] - totals[2]} unaudited-or-stale"
    )
    lines.append("No locator means unclassified: it does not imply missing or PDF-only evidence.")
    return "\n".join(lines)
