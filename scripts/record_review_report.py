#!/usr/bin/env python3
"""Consolidate remaining-record reviews without certifying their claims.

The report is an editorial inventory: it preserves reviewer scope, evidence,
and historical findings while separately tracking current model fingerprints
and numeric bindings. It never reads samples unless ``--samples`` is supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "samples" / "remaining-audit-20261028"
DATA = REPO / "data"
DEFAULT_OUTPUT = REPO / "docs" / "audits" / "20261028-remaining-records.json"
QUEUE_FILES = ("early_us.json", "middle_us.json", "recent_us.json", "world.json")
REVIEW_FILES = (
    "early_us-results.json",
    "world-results.json",
    "recent_us-results.json",
    "early_us-middle-addenda.json",
    "early_us-special-addenda.json",
    "early_us-consumption-addenda.json",
    "early_us-final-addenda.json",
    "world-middle-addenda.json",
    "world-recent-addenda.json",
    "middle-us-health-food-results.json",
    "root-reserved-results.json",
    "root-car-price-results.json",
    "root-vehicle-results.json",
    "root-early-scope-results.json",
    "root-world-scope-results.json",
    "root-final-source-results.json",
    "root-early-full-results.json",
    "root-middle-full-results.json",
    "root-recent-full-results.json",
    "root-reconstruction-20261029-results.json",
)
EXPECTED_BASELINE_COUNT = 561
EXPECTED_BASELINE_ID_FINGERPRINT = (
    "0a898fde09169f38b43a08c4627b8f3684bcc19247219830fa0ff52967a37d33"
)
DISPOSITIONS = {"source_reviewed", "curation_gap", "computed_in_code", "needs_source", "unresolved"}
REVIEW_STATUSES = {
    "verified",
    "correction",
    "corrected",
    "partial",
    "gap_reviewed",
    "needs_source",
    "pending",
}


class ReportError(ValueError):
    """Input reports cannot be reconciled safely."""


def validate_sha256_pin(value: Any, *, context: str) -> None:
    """Require a canonical lowercase SHA-256 pin before comparing bytes."""
    if value is None:
        return
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ReportError(f"{context}: sha256 must be exactly 64 lowercase hexadecimal characters")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReportError(f"cannot read JSON report {path}: {exc}") from exc


def _records(document: Any, report: str) -> list[dict[str, Any]]:
    if isinstance(document, list):
        records = document
    elif isinstance(document, dict):
        records = document.get("results", document.get("records"))
    else:
        records = None
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        raise ReportError(f"{report}: expected a list or an object containing results/records")
    return records


def load_baseline(samples_dir: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    """Load all baseline records and preserve their original fingerprints."""
    baseline: dict[str, dict[str, Any]] = {}
    diagnostics: list[dict[str, str]] = []
    for filename in QUEUE_FILES:
        path = samples_dir / filename
        if not path.is_file():
            raise ReportError(f"missing baseline queue: {path}")
        records = _records(_read_json(path), filename)
        for record in records:
            fact = record.get("fact")
            if not isinstance(fact, dict) or not isinstance(fact.get("id"), str):
                raise ReportError(f"{filename}: baseline entry has no fact.id")
            fact_id = fact["id"]
            if fact_id in baseline:
                raise ReportError(f"duplicate baseline ID {fact_id!r} in {filename}")
            fingerprint = record.get("fingerprint")
            if not isinstance(fingerprint, str) or not fingerprint:
                raise ReportError(f"{filename}: {fact_id} has no baseline fingerprint")
            baseline[fact_id] = {
                "fact_id": fact_id,
                "queue": filename,
                "room": record.get("room", ""),
                "baseline_fingerprint": fingerprint,
                "baseline_entity_type": "Fact",
                "gap_at_baseline": bool(record.get("gap", False)),
            }
    if len(baseline) != 561:
        diagnostics.append(
            {
                "kind": "baseline_count_mismatch",
                "message": f"Expected 561 baseline IDs; found {len(baseline)}.",
            }
        )
    return baseline, diagnostics


def collect_reviews(
    samples_dir: Path, baseline_ids: set[str]
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, str]]]:
    """Normalize report containers; reject duplicates rather than choosing silently."""
    reviews: dict[str, list[dict[str, Any]]] = {}
    diagnostics: list[dict[str, str]] = []
    for filename in REVIEW_FILES:
        path = samples_dir / filename
        if not path.is_file():
            diagnostics.append(
                {
                    "kind": "missing_review_report",
                    "report": filename,
                    "message": (
                        f"Review report {filename} is not present; affected IDs remain unresolved."
                    ),
                }
            )
            continue
        rows = _records(_read_json(path), filename)
        seen: set[str] = set()
        for row in rows:
            fact_id = row.get("fact_id", row.get("id"))
            if not isinstance(fact_id, str) or not fact_id:
                raise ReportError(f"{filename}: review entry has no fact_id")
            if fact_id in seen:
                raise ReportError(f"duplicate review ID {fact_id!r} within {filename}")
            seen.add(fact_id)
            if fact_id not in baseline_ids:
                raise ReportError(
                    f"{filename}: review ID {fact_id!r} is not in the baseline queues"
                )
            status = row.get("status")
            if not isinstance(status, str) or not status:
                raise ReportError(f"{filename}: {fact_id} has no review status")
            checked = row.get("checked_fields", [])
            evidence = row.get("evidence", [])
            issues = row.get("issues", [])
            if not isinstance(checked, list) or not all(isinstance(v, str) for v in checked):
                raise ReportError(f"{filename}: {fact_id} checked_fields must be a list of strings")
            if not isinstance(evidence, list) or not all(isinstance(v, dict) for v in evidence):
                raise ReportError(f"{filename}: {fact_id} evidence must be a list of objects")
            for evidence_index, evidence_item in enumerate(evidence):
                validate_sha256_pin(
                    evidence_item.get("sha256"),
                    context=f"{filename}: {fact_id} evidence[{evidence_index}]",
                )
            if not isinstance(issues, list) or not all(isinstance(v, str) for v in issues):
                raise ReportError(f"{filename}: {fact_id} issues must be a list of strings")
            review_fingerprint = row.get("original_fingerprint", row.get("fingerprint"))
            reviewed_current_fingerprint = row.get(
                "reviewed_current_fingerprint", row.get("current_fingerprint")
            )
            normalized = {
                "report": filename,
                "review_status": status,
                "review_fingerprint": review_fingerprint,
                "checked_fields": checked,
                "historical_findings": issues,
                "evidence": evidence,
                "proposed_changes": row.get("proposed_changes", {}),
                "proposed_audit": row.get("proposed_audit"),
                "acquisition": row.get("acquisition"),
            }
            if reviewed_current_fingerprint is not None:
                normalized["reviewed_current_fingerprint"] = reviewed_current_fingerprint
            reviews.setdefault(fact_id, []).append(normalized)
    return reviews, diagnostics


def _json_default(value: object) -> str:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(type(value).__name__)


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=_json_default,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def baseline_id_fingerprint(records: list[dict[str, Any]]) -> str:
    """Pin the queue and ID membership independently of ignored review inputs."""
    membership = sorted(
        (row["queue"], row["fact_id"])
        for row in records
        if isinstance(row.get("queue"), str) and isinstance(row.get("fact_id"), str)
    )
    encoded = json.dumps(
        membership, ensure_ascii=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def current_entity_fingerprints(data_dir: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Resolve current facts/derived facts and bind meaning plus operands."""
    # Imports stay inside the function so safety/path helpers remain stdlib-only.
    from vitrine.audit import fingerprint as fact_fingerprint
    from vitrine.loader import load_corpus
    from vitrine.series import load_series

    corpus = load_corpus(data_dir)
    facts = {fact.id: fact for room in corpus.rooms for fact in room.facts}
    derived = {item.id: item for room in corpus.rooms for item in room.derived}
    if set(facts) & set(derived):
        raise ReportError("current data contains IDs that are both Fact and DerivedFact")
    series = load_series(data_dir)
    source_hashes = {sid: _canonical_hash(asdict(source)) for sid, source in corpus.sources.items()}
    fact_hashes: dict[str, str | None] = {}
    diagnostics: list[dict[str, str]] = []
    for fid, fact in facts.items():
        missing = []
        if fact.source not in corpus.sources:
            missing.append(f"source:{fact.source}")
        missing.extend(
            f"assumption:{item}" for item in fact.assumptions if item not in corpus.assumptions
        )
        if missing:
            fact_hashes[fid] = None
            diagnostics.append(
                {
                    "kind": "unresolved_current_references",
                    "fact_id": fid,
                    "message": (
                        "Current fingerprint unavailable; unresolved reference(s): "
                        f"{', '.join(missing)}."
                    ),
                }
            )
        else:
            fact_hashes[fid] = fact_fingerprint(corpus, fact)
    current: dict[str, dict[str, Any]] = {}
    for fid, fact in facts.items():
        current[fid] = {
            "entity_type": "Fact",
            "current_fingerprint": fact_hashes[fid],
            "source_fingerprint": source_hashes.get(fact.source),
            "audit_ref": fact.audit is not None,
            "audit_entry": None,
            "fact": fact,
        }
    for fid, item in derived.items():
        operands: list[dict[str, str | None]] = []
        for operand_id in dict.fromkeys((item.numerator, item.denominator)):
            if not operand_id:
                continue
            operand = facts.get(operand_id)
            operands.append(
                {
                    "id": operand_id,
                    "fingerprint": fact_hashes.get(operand_id),
                    "source_fingerprint": source_hashes.get(operand.source) if operand else None,
                }
            )
        series_ids = tuple(
            dict.fromkeys(
                ([item.inflate_series] if item.inflate_series else []) + list(item.count_series)
            )
        )
        series_refs: list[dict[str, str | None]] = []
        for series_id in series_ids:
            item_series = series.get(series_id)
            series_source = item_series.source if item_series else ""
            series_refs.append(
                {
                    "id": series_id,
                    "fingerprint": _canonical_hash(asdict(item_series)) if item_series else None,
                    "source_fingerprint": source_hashes.get(series_source),
                }
            )
        references_resolve = (
            all(operand.get("fingerprint") is not None for operand in operands)
            and all(item.get("source_fingerprint") is not None for item in operands)
            and all(
                item.get("fingerprint") is not None and item.get("source_fingerprint") is not None
                for item in series_refs
            )
            and all(assumption in corpus.assumptions for assumption in item.assumptions)
        )
        if not references_resolve:
            diagnostics.append(
                {
                    "kind": "unresolved_derived_references",
                    "fact_id": fid,
                    "message": (
                        "Current DerivedFact fingerprint unavailable because an operand, "
                        "series, source, or assumption does not resolve."
                    ),
                }
            )
        current[fid] = {
            "entity_type": "DerivedFact",
            "current_fingerprint": _canonical_hash(
                {"derived": asdict(item), "operands": operands, "series": series_refs}
            )
            if references_resolve
            else None,
            "source_fingerprint": None,
            "audit_ref": False,
            "audit_entry": None,
            "derived": item,
            "operands": operands,
            "series": series_refs,
        }
    ledger = {entry.fact_id: entry for entry in corpus.audit_ledger}
    for fid, item in current.items():
        entry = ledger.get(fid)
        item["audit_entry"] = entry
    return current, {"ledger": ledger, "diagnostics": diagnostics}


def _disposition(entity_type: str | None, latest: dict[str, Any] | None) -> str:
    if latest is None or entity_type is None:
        return "unresolved"
    status = latest["review_status"]
    if status == "needs_source":
        return "needs_source"
    if status == "pending":
        return "unresolved"
    if status == "gap_reviewed":
        return "curation_gap"
    if entity_type == "DerivedFact":
        return "computed_in_code"
    if status in {"verified", "correction", "corrected", "partial"}:
        return "source_reviewed"
    return "unresolved"


def _numeric_binding(entity: dict[str, Any] | None, fact_id: str) -> dict[str, Any]:
    if entity is None:
        return {
            "status": "entity_missing",
            "explanation": "No current Fact or DerivedFact resolves this ID.",
        }
    if entity["entity_type"] == "DerivedFact":
        return {
            "status": "computed_in_code",
            "explanation": (
                "The value is derived by repository code from the recorded operands/series."
            ),
            "operands": entity.get("operands", []),
            "series": entity.get("series", []),
        }
    fact = entity["fact"]
    entry = entity.get("audit_entry")
    if fact.audit is None:
        return {
            "status": "no_audit_ref",
            "explanation": "No guarded numeric field binding is authored on this Fact.",
        }
    if entry is None:
        return {
            "status": "audit_entry_missing",
            "explanation": "Fact has an audit reference but no current ledger entry.",
        }
    if entry.fingerprint != entity["current_fingerprint"]:
        return {
            "status": "stale_fingerprint",
            "explanation": (
                "Ledger entry fingerprint does not match the current Fact and source meaning."
            ),
        }
    return {
        "status": "bound_current",
        "explanation": (
            "The ledger entry fingerprint matches the current Fact; this binds transcription, "
            "not interpretation."
        ),
        "file": fact.audit.file,
        "extractor": fact.audit.extractor.value,
        "locator": fact.audit.locator,
        "sample_sha256": entry.sample_sha256,
    }


def safe_sample_path(samples_root: Path, relative: str) -> Path:
    """Resolve one explicit sample locator without allowing traversal/secrets."""
    if not isinstance(relative, str) or not relative:
        raise ValueError("sample evidence path must be a non-empty string")
    if "\\" in relative or ":" in relative or any(ord(char) < 32 for char in relative):
        raise ValueError("sample evidence path is not a normalized POSIX relative path")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
        raise ValueError("sample evidence path is absolute, traversing, or not normalized")
    if any(
        ".env" in part.casefold() or part.casefold().startswith("privateconfig")
        for part in pure.parts
    ):
        raise ValueError("secret/private configuration paths are never evidence files")
    root = samples_root.resolve()
    target = root.joinpath(*pure.parts).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("sample evidence path escapes samples root") from exc
    return target


def _evidence_checks(
    reviews: list[dict[str, Any]], samples_root: Path, *, hash_files: bool = False
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    checks: list[dict[str, Any]] = []
    attention: list[dict[str, str]] = []
    for review in reviews:
        for evidence in review["evidence"]:
            report = review["report"]
            locator = evidence.get("file", evidence.get("path"))
            raw_files = evidence.get("original_files", [])
            if isinstance(raw_files, str):
                raw_files = [raw_files]
            file_refs: list[tuple[str, str | None]] = []
            if isinstance(locator, str):
                file_refs.append((locator, evidence.get("sha256")))
            if isinstance(raw_files, list):
                file_refs.extend((item, None) for item in raw_files if isinstance(item, str))
            url = evidence.get("url")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                attention.append({"report": report, "url": url, "kind": "unarchived_web_url"})
                checks.append({"report": report, "url": url, "status": "not_archived_url"})
            for raw, expected_hash in file_refs:
                if not isinstance(raw, str):
                    attention.append(
                        {
                            "report": report,
                            "kind": "invalid_evidence_path",
                            "detail": "path was not a string",
                        }
                    )
                    continue
                if raw.startswith(("http://", "https://")):
                    attention.append({"report": report, "url": raw, "kind": "unarchived_web_url"})
                    checks.append({"report": report, "url": raw, "status": "not_archived_url"})
                    continue
                try:
                    target = safe_sample_path(samples_root, raw)
                except ValueError as exc:
                    attention.append(
                        {"report": report, "kind": "unsafe_evidence_path", "detail": str(exc)}
                    )
                    checks.append({"report": report, "file": raw, "status": "unsafe_path"})
                    continue
                if not hash_files:
                    checks.append(
                        {
                            "report": report,
                            "file": raw,
                            "status": "normalized_relative_path",
                        }
                    )
                    continue
                if not target.is_file():
                    checks.append({"report": report, "file": raw, "status": "missing"})
                    continue
                observed_hash = hashlib.sha256(target.read_bytes()).hexdigest()
                check = {
                    "report": report,
                    "file": raw,
                    "status": "observed_current_hash",
                    "observed_current_hash": observed_hash,
                    "hash_origin": "consolidation_time",
                    "reported_original_pin": None,
                }
                if isinstance(expected_hash, str):
                    check["reported_original_pin"] = expected_hash
                    check["status"] = (
                        "hash_matches" if observed_hash == expected_hash else "hash_mismatch"
                    )
                checks.append(check)
    return checks, attention


def build_manifest(
    samples_dir: Path,
    data_dir: Path,
    *,
    hash_samples: bool = False,
    evidence_samples_dir: Path | None = None,
) -> dict[str, Any]:
    baseline, diagnostics = load_baseline(samples_dir)
    reviews, review_diagnostics = collect_reviews(samples_dir, set(baseline))
    diagnostics.extend(review_diagnostics)
    current, current_context = current_entity_fingerprints(data_dir)
    diagnostics.extend(current_context["diagnostics"])
    records: list[dict[str, Any]] = []
    for fact_id in sorted(baseline):
        base = baseline[fact_id]
        all_reviews = reviews.get(fact_id, [])
        entity = current.get(fact_id)
        latest = all_reviews[-1] if all_reviews else None
        if entity is None:
            diagnostics.append(
                {
                    "kind": "missing_current_entity",
                    "fact_id": fact_id,
                    "message": "Baseline ID does not resolve to a current Fact or DerivedFact.",
                }
            )
        review_rows: list[dict[str, Any]] = []
        flattened_evidence: list[dict[str, Any]] = []
        for review in all_reviews:
            match = review["review_fingerprint"] == base["baseline_fingerprint"]
            review_row = {
                "report": review["report"],
                "review_status": review["review_status"],
                "review_fingerprint": review["review_fingerprint"],
                "matches_baseline_fingerprint": match,
                "scope_fields": review["checked_fields"],
                "historical_findings": review["historical_findings"],
                "proposed_changes": review["proposed_changes"],
                "proposed_audit": review["proposed_audit"],
                "acquisition": review["acquisition"],
            }
            if "reviewed_current_fingerprint" in review:
                review_row["reviewed_current_fingerprint"] = review[
                    "reviewed_current_fingerprint"
                ]
            review_rows.append(review_row)
            for evidence in review["evidence"]:
                flattened_evidence.append({"report": review["report"], **evidence})
        record = {
            **base,
            "entity_type": entity["entity_type"] if entity else "missing_current_entity",
            "current_fingerprint": entity["current_fingerprint"] if entity else None,
            "current_matches_baseline_fingerprint": bool(
                entity and entity["current_fingerprint"] == base["baseline_fingerprint"]
            ),
            "disposition": _disposition(entity["entity_type"] if entity else None, latest),
            "review_status_latest": latest["review_status"] if latest else None,
            "review_report_latest": latest["report"] if latest else None,
            "scope_fields_latest": latest["checked_fields"] if latest else [],
            "historical_findings": [
                {"report": item["report"], "items": item["historical_findings"]}
                for item in all_reviews
                if item["historical_findings"]
            ],
            "reviews": review_rows,
            "evidence": flattened_evidence,
            "numeric_field_binding": _numeric_binding(entity, fact_id),
        }
        checks, attention = _evidence_checks(
            all_reviews,
            evidence_samples_dir or samples_dir.parent,
            hash_files=hash_samples,
        )
        record["evidence_checks"] = checks
        if attention:
            record["evidence_attention"] = attention
        records.append(record)
    counts = Counter(record["disposition"] for record in records)
    if set(counts) - DISPOSITIONS:
        raise ReportError("internal error: unsupported disposition emitted")
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "purpose": (
            "Editorial review inventory; it records review scope and current bindings, "
            "not source re-verification."
        ),
        "status_semantics": {
            "source_reviewed": (
                "A source review record exists for the Fact. Review status and checked scope are "
                "retained; partial means unchecked fields are not certified. This disposition "
                "does not certify the full Fact or its interpretation."
            ),
            "curation_gap": "The reviewed record is a gap rather than a numeric claim.",
            "computed_in_code": (
                "The current entity is a DerivedFact computed from its recorded operands."
            ),
            "needs_source": (
                "The latest review identifies a specific missing or inaccessible source."
            ),
            "unresolved": "No usable review is present, or the current entity does not resolve.",
        },
        "historical_findings_note": (
            "Reviewer issues are copied as historical findings; "
            "they are not automatically current defects."
        ),
        "evidence_note": (
            "Evidence locators and short support text are copied from review records. Optional "
            "sample hashing checks file presence and bytes only; it does not re-read or certify "
            "source meaning, population fit, or the Fact."
        ),
        "numeric_binding_note": (
            "Numeric field binding is tracked separately from source review. "
            "A current ledger binding "
            "checks transcription identity, not source interpretation or population fit."
        ),
        "baseline_count": len(baseline),
        "baseline_id_fingerprint": baseline_id_fingerprint(records),
        "reviewed_unique_count": len(reviews),
        "disposition_counts": dict(sorted(counts.items())),
        "diagnostics": diagnostics,
        "records": records,
    }
    if hash_samples:
        manifest["sample_hashing"] = (
            "Only explicit evidence paths were checked; URLs are flagged as unarchived "
            "and no source content was interpreted."
        )
    return manifest


def check_manifest(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    """Check membership and current fingerprints without reading samples."""
    errors: list[str] = []
    expected_records = {r["fact_id"]: r for r in expected.get("records", [])}
    actual_records = {r["fact_id"]: r for r in actual.get("records", [])}
    if len(expected_records) != len(expected.get("records", [])):
        errors.append("generated manifest contains duplicate fact IDs")
    if len(actual_records) != len(actual.get("records", [])):
        errors.append("saved manifest contains duplicate fact IDs")
    if expected_records.keys() != actual_records.keys():
        errors.append("saved manifest baseline membership is stale")
    for fact_id in expected_records.keys() & actual_records.keys():
        current_expected = expected_records[fact_id].get("current_fingerprint")
        current_actual = actual_records[fact_id].get("current_fingerprint")
        if current_expected is None:
            errors.append(f"{fact_id}: current fingerprint cannot be resolved")
        if current_expected != current_actual:
            errors.append(f"{fact_id}: current fingerprint is stale")
        if expected_records[fact_id].get("baseline_fingerprint") != actual_records[fact_id].get(
            "baseline_fingerprint"
        ):
            errors.append(f"{fact_id}: baseline fingerprint changed")
    return errors


def check_saved_manifest(saved: dict[str, Any], data_dir: Path) -> list[str]:
    """Check the committed inventory against repository data, without queue inputs."""
    errors: list[str] = []
    records = saved.get("records")
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        return ["saved manifest records must be a list of objects"]
    by_id: dict[str, dict[str, Any]] = {}
    for row in records:
        fact_id = row.get("fact_id")
        if not isinstance(fact_id, str) or not fact_id:
            errors.append("saved manifest record has no fact_id")
            continue
        if fact_id in by_id:
            errors.append(f"saved manifest has duplicate fact ID {fact_id}")
        by_id[fact_id] = row
        if not isinstance(row.get("baseline_fingerprint"), str) or not row[
            "baseline_fingerprint"
        ]:
            errors.append(f"{fact_id}: baseline fingerprint is missing")
        if row.get("queue") not in QUEUE_FILES:
            errors.append(f"{fact_id}: baseline queue is invalid")
        if row.get("disposition") not in DISPOSITIONS:
            errors.append(f"{fact_id}: disposition is invalid")
        latest_scope = row.get("scope_fields_latest")
        if not isinstance(latest_scope, list) or not all(
            isinstance(item, str) for item in latest_scope
        ):
            errors.append(f"{fact_id}: latest review scope is malformed")
        evidence = row.get("evidence")
        if not isinstance(evidence, list) or not all(
            isinstance(item, dict) and isinstance(item.get("report"), str) for item in evidence
        ):
            errors.append(f"{fact_id}: evidence inventory is malformed")
        reviews = row.get("reviews")
        if not isinstance(reviews, list):
            errors.append(f"{fact_id}: review history is malformed")
        else:
            review_reports: set[str] = set()
            for review in reviews:
                if not isinstance(review, dict) or not isinstance(review.get("report"), str):
                    errors.append(f"{fact_id}: review provenance is malformed")
                    continue
                review_reports.add(review["report"])
                if review.get("review_status") not in REVIEW_STATUSES:
                    errors.append(f"{fact_id}: review status is invalid")
                declared_current = review.get("reviewed_current_fingerprint")
                if declared_current is not None and (
                    not isinstance(declared_current, str) or not declared_current
                ):
                    errors.append(f"{fact_id}: declared reviewed current fingerprint is malformed")
                scope = review.get("scope_fields")
                if not isinstance(scope, list) or not all(isinstance(item, str) for item in scope):
                    errors.append(f"{fact_id}: review scope is malformed")
            if reviews:
                latest = reviews[-1]
                if row.get("review_status_latest") != latest.get("review_status"):
                    errors.append(f"{fact_id}: latest review status is inconsistent")
                if row.get("review_report_latest") != latest.get("report"):
                    errors.append(f"{fact_id}: latest review report is inconsistent")
                if row.get("scope_fields_latest") != latest.get("scope_fields"):
                    errors.append(f"{fact_id}: latest review scope is inconsistent")
            elif any(
                row.get(field) is not None
                for field in ("review_status_latest", "review_report_latest")
            ) or row.get("scope_fields_latest"):
                errors.append(f"{fact_id}: latest review fields exist without review history")
            for item in evidence if isinstance(evidence, list) else []:
                if isinstance(item, dict) and item.get("report") not in review_reports:
                    errors.append(f"{fact_id}: evidence cites no retained review")
    expected_count = saved.get("baseline_count")
    if expected_count != EXPECTED_BASELINE_COUNT or len(by_id) != EXPECTED_BASELINE_COUNT:
        errors.append(
            f"saved manifest must contain exactly {EXPECTED_BASELINE_COUNT} unique baseline IDs"
        )
    actual_membership_fingerprint = baseline_id_fingerprint(records)
    if saved.get("baseline_id_fingerprint") != actual_membership_fingerprint:
        errors.append("saved manifest baseline ID fingerprint is stale")
    if actual_membership_fingerprint != EXPECTED_BASELINE_ID_FINGERPRINT:
        errors.append("saved manifest IDs do not match the pinned baseline queues")
    reviewed_count = sum(bool(row.get("reviews")) for row in by_id.values())
    if saved.get("reviewed_unique_count") != reviewed_count:
        errors.append("saved manifest reviewed_unique_count does not match review histories")

    try:
        current, _ = current_entity_fingerprints(data_dir)
    except (OSError, ValueError, KeyError) as exc:
        errors.append(f"current repository data cannot be loaded: {exc}")
        return errors
    for fact_id, row in by_id.items():
        entity = current.get(fact_id)
        if entity is None:
            errors.append(f"{fact_id}: current entity is missing")
            continue
        actual = entity.get("current_fingerprint")
        if actual is None:
            errors.append(f"{fact_id}: current fingerprint cannot be resolved")
        elif row.get("current_fingerprint") != actual:
            errors.append(f"{fact_id}: current fingerprint is stale")
        reviews = row.get("reviews")
        if isinstance(reviews, list) and reviews:
            latest = reviews[-1]
            if isinstance(latest, dict):
                reviewed_current = latest.get("reviewed_current_fingerprint")
                if reviewed_current is not None and reviewed_current != actual:
                    errors.append(
                        f"{fact_id}: latest review current fingerprint is stale"
                    )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"manifest path (default: {DEFAULT_OUTPUT.relative_to(REPO)})",
    )
    parser.add_argument(
        "--samples-dir",
        type=Path,
        default=SAMPLES,
        help="directory containing the baseline queues and review reports",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA,
        help="current vitrine data directory used for entity fingerprints",
    )
    parser.add_argument(
        "--evidence-samples-dir",
        type=Path,
        help="samples root for explicit evidence files (defaults to the queue samples root)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "validate saved baseline, review scopes, and current fingerprints "
            "without sample inputs"
        ),
    )
    parser.add_argument(
        "--samples",
        action="store_true",
        help="hash only explicit evidence files and flag unarchived URLs",
    )
    args = parser.parse_args(argv)
    try:
        if args.check:
            saved = _read_json(args.output)
            if not isinstance(saved, dict):
                raise ReportError("saved manifest must be a JSON object")
            errors = check_saved_manifest(saved, args.data_dir)
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            print(
                f"OK: {args.output} has {saved['baseline_count']} unique baseline IDs; "
                "review scopes are valid and current fingerprints match."
            )
            return 0
        generated = build_manifest(
            args.samples_dir,
            args.data_dir,
            hash_samples=args.samples,
            evidence_samples_dir=args.evidence_samples_dir,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(generated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"Wrote {args.output} ({generated['baseline_count']} IDs; "
            f"{generated['reviewed_unique_count']} reviewed)."
        )
        print(json.dumps(generated["disposition_counts"], sort_keys=True))
        for diagnostic in generated["diagnostics"]:
            print(
                f"DIAGNOSTIC: {diagnostic.get('message', diagnostic.get('kind'))}",
                file=sys.stderr,
            )
        return 0
    except (ReportError, OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
