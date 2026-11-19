"""Synthetic checks for the remaining-record review inventory."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from record_review_report import (
    REVIEW_FILES,
    ReportError,
    _evidence_checks,
    baseline_id_fingerprint,
    check_manifest,
    check_saved_manifest,
    collect_reviews,
    current_entity_fingerprints,
    safe_sample_path,
    validate_sha256_pin,
)


def _write_minimal_data(
    root: Path,
    *,
    source_population: str = "workers",
    fact_notes: str = "checked",
    derived_op: str = "quantity_ratio",
) -> None:
    (root / "us").mkdir(parents=True, exist_ok=True)
    (root / "series").mkdir(exist_ok=True)
    (root / "sources.toml").write_text(
        "[[source]]\nid = 'test'\ntitle = 'Test source'\npublisher = 'Test'\n"
        "year = 1950\nurl = 'https://example.test/source'\n"
        f"population = '{source_population}'\n",
        encoding="utf-8",
    )
    (root / "assumptions.toml").write_text("", encoding="utf-8")
    (root / "audit-ledger.toml").write_text("version = 2\n", encoding="utf-8")
    (root / "us" / "1950s.toml").write_text(
        "[room]\ncountry = 'us'\ndecade = '1950s'\n\n"
        "[[fact]]\nid = 'us-1950s-a'\npanel = 'table'\nlabel = 'A'\n"
        "value = '5'\nunit = 'count'\nsource = 'test'\ntier = 'A'\n"
        f"notes = '{fact_notes}'\nquantity = 5\n\n"
        "[[fact]]\nid = 'us-1950s-b'\npanel = 'table'\nlabel = 'B'\n"
        "value = '2'\nunit = 'count'\nsource = 'test'\ntier = 'A'\nquantity = 2\n\n"
        "[[derived]]\nid = 'us-1950s-ratio'\npanel = 'table'\nlabel = 'Ratio'\n"
        "unit = 'ratio'\n"
        f"op = '{derived_op}'\n"
        "numerator = 'us-1950s-a'\ndenominator = 'us-1950s-b'\n",
        encoding="utf-8",
    )


def test_source_fact_and_derived_method_changes_make_current_fingerprints_stale(
    tmp_path: Path,
) -> None:
    _write_minimal_data(tmp_path)
    original, _ = current_entity_fingerprints(tmp_path)

    _write_minimal_data(tmp_path, source_population="employees")
    changed_source, _ = current_entity_fingerprints(tmp_path)
    assert (
        changed_source["us-1950s-a"]["current_fingerprint"]
        != original["us-1950s-a"]["current_fingerprint"]
    )

    _write_minimal_data(tmp_path, fact_notes="revised scope")
    changed_fact, _ = current_entity_fingerprints(tmp_path)
    assert (
        changed_fact["us-1950s-a"]["current_fingerprint"]
        != original["us-1950s-a"]["current_fingerprint"]
    )

    _write_minimal_data(tmp_path, derived_op="ratio")
    changed_method, _ = current_entity_fingerprints(tmp_path)
    assert (
        changed_method["us-1950s-ratio"]["current_fingerprint"]
        != original["us-1950s-ratio"]["current_fingerprint"]
    )


def test_review_input_accepts_list_and_results_object_and_keeps_partial_scope(
    tmp_path: Path,
) -> None:
    (tmp_path / "early_us-results.json").write_text(
        json.dumps(
            {
                "results": [
                    {
                        "fact_id": "us-1950s-a",
                        "original_fingerprint": "base-a",
                        "reviewed_current_fingerprint": "current-a",
                        "status": "partial",
                        "checked_fields": ["value"],
                        "issues": ["A historical note."],
                        "evidence": [{"file": "source.csv", "locator": "row 4"}],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "world-results.json").write_text(
        json.dumps(
            [
                {
                    "fact_id": "us-1950s-b",
                    "fingerprint": "base-b",
                    "current_fingerprint": "current-b",
                    "status": "verified",
                    "checked_fields": ["value", "population"],
                    "evidence": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    reviews, diagnostics = collect_reviews(tmp_path, {"us-1950s-a", "us-1950s-b"})
    assert len(diagnostics) == len(REVIEW_FILES) - 2
    assert all(item["kind"] == "missing_review_report" for item in diagnostics)
    assert reviews["us-1950s-a"][0]["review_status"] == "partial"
    assert reviews["us-1950s-a"][0]["checked_fields"] == ["value"]
    assert reviews["us-1950s-a"][0]["reviewed_current_fingerprint"] == "current-a"
    assert reviews["us-1950s-a"][0]["historical_findings"] == ["A historical note."]
    assert reviews["us-1950s-b"][0]["review_fingerprint"] == "base-b"
    assert reviews["us-1950s-b"][0]["reviewed_current_fingerprint"] == "current-b"
    assert (
        len([name for name in REVIEW_FILES if not (tmp_path / name).exists()])
        == len(REVIEW_FILES) - 2
    )


def test_duplicate_id_within_one_report_is_rejected(tmp_path: Path) -> None:
    row = {"fact_id": "us-1950s-a", "status": "verified", "checked_fields": [], "evidence": []}
    (tmp_path / "early_us-results.json").write_text(json.dumps([row, row]), encoding="utf-8")
    with pytest.raises(ReportError, match="duplicate review ID"):
        collect_reviews(tmp_path, {"us-1950s-a"})


def test_review_id_missing_from_baseline_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "early_us-results.json").write_text(
        json.dumps(
            [
                {
                    "fact_id": "not-in-baseline",
                    "status": "verified",
                    "checked_fields": [],
                    "evidence": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ReportError, match="not in the baseline queues"):
        collect_reviews(tmp_path, {"us-1950s-a"})


@pytest.mark.parametrize("length", [63, 65])
def test_malformed_sha256_pin_is_rejected_before_sample_comparison(length: int) -> None:
    with pytest.raises(ReportError, match="exactly 64 lowercase hexadecimal characters"):
        validate_sha256_pin("a" * length, context="synthetic evidence")


def test_valid_sha256_pin_requires_lowercase_hex() -> None:
    validate_sha256_pin("a" * 64, context="synthetic evidence")
    with pytest.raises(ReportError, match="exactly 64 lowercase hexadecimal characters"):
        validate_sha256_pin("A" * 64, context="synthetic evidence")


@pytest.mark.parametrize("length", [63, 65])
def test_report_rejects_malformed_evidence_pin_before_hashing(
    tmp_path: Path,
    length: int,
) -> None:
    (tmp_path / "early_us-results.json").write_text(
        json.dumps(
            [
                {
                    "fact_id": "us-1950s-a",
                    "status": "verified",
                    "checked_fields": [],
                    "evidence": [{"file": "not-read.csv", "sha256": "a" * length}],
                }
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ReportError, match=r"evidence\[0\].*exactly 64 lowercase"):
        collect_reviews(tmp_path, {"us-1950s-a"})


@pytest.mark.parametrize(
    "relative",
    [
        "../api.env",
        "privateconfig/credentials.json",
        "privateconfig.json",
        "api.env",
        "secret.env.local",
        "..\\api.env",
        "C:/private/data",
    ],
)
def test_sample_evidence_paths_reject_traversal_and_private_config(
    tmp_path: Path,
    relative: str,
) -> None:
    with pytest.raises(ValueError):
        safe_sample_path(tmp_path, relative)


def test_check_manifest_detects_stale_fact_fingerprint_and_membership() -> None:
    expected = {
        "records": [
            {"fact_id": "a", "baseline_fingerprint": "base", "current_fingerprint": "current"}
        ]
    }
    saved = {
        "records": [
            {"fact_id": "a", "baseline_fingerprint": "base", "current_fingerprint": "stale"}
        ]
    }
    assert check_manifest(expected, saved) == ["a: current fingerprint is stale"]
    saved["records"].append({"fact_id": "extra"})
    assert "saved manifest baseline membership is stale" in check_manifest(expected, saved)


def test_saved_manifest_check_uses_only_manifest_and_current_data(
    monkeypatch, tmp_path: Path
) -> None:
    import record_review_report as report_module

    records = [
        {
            "fact_id": f"us-1950s-fact-{number}",
            "queue": "early_us.json",
            "baseline_fingerprint": f"baseline-{number}",
            "current_fingerprint": f"current-{number}",
            "disposition": "unresolved",
            "scope_fields_latest": [],
            "reviews": [],
            "evidence": [],
        }
        for number in range(561)
    ]
    monkeypatch.setattr(
        report_module,
        "EXPECTED_BASELINE_ID_FINGERPRINT",
        baseline_id_fingerprint(records),
    )
    monkeypatch.setattr(
        report_module,
        "current_entity_fingerprints",
        lambda _data_dir: (
            {
                row["fact_id"]: {"current_fingerprint": f"current-{number}"}
                for number, row in enumerate(records)
            },
            {},
        ),
    )
    manifest = {
        "baseline_count": 561,
        "baseline_id_fingerprint": baseline_id_fingerprint(records),
        "reviewed_unique_count": 0,
        "records": records,
    }
    records[0]["reviews"] = [
        {
            "report": "older.json",
            "review_status": "partial",
            "reviewed_current_fingerprint": "old-current-fingerprint",
            "scope_fields": ["value"],
        },
        {
            "report": "latest.json",
            "review_status": "verified",
            "reviewed_current_fingerprint": "current-0",
            "scope_fields": ["value", "population"],
        },
    ]
    records[0]["review_status_latest"] = "verified"
    records[0]["review_report_latest"] = "latest.json"
    records[0]["scope_fields_latest"] = ["value", "population"]
    manifest["reviewed_unique_count"] = 1
    # Historical review snapshots may predate later legitimate edits. Only the
    # latest review's explicitly declared current fingerprint must be fresh.
    assert check_saved_manifest(manifest, tmp_path) == []
    records[0]["reviews"][-1]["reviewed_current_fingerprint"] = "stale-review"
    assert check_saved_manifest(manifest, tmp_path) == [
        f"{records[0]['fact_id']}: latest review current fingerprint is stale"
    ]
    records[0]["reviews"][-1]["reviewed_current_fingerprint"] = "current-0"
    manifest["records"][0]["current_fingerprint"] = "stale"
    assert check_saved_manifest(manifest, tmp_path) == [
        f"{records[0]['fact_id']}: current fingerprint is stale"
    ]
    manifest["records"][0]["current_fingerprint"] = "current-0"
    manifest["records"][0]["queue"] = "middle_us.json"
    assert "saved manifest IDs do not match the pinned baseline queues" in check_saved_manifest(
        manifest, tmp_path
    )


def test_safe_sample_path_accepts_normalized_relative_path(tmp_path: Path) -> None:
    target = tmp_path / "archive" / "table.csv"
    target.parent.mkdir()
    target.write_text("year,value\n1950,5\n", encoding="utf-8")
    assert safe_sample_path(tmp_path, "archive/table.csv") == target.resolve()


def test_optional_sample_check_hashes_only_explicit_files_and_flags_urls(
    tmp_path: Path,
) -> None:
    sample = tmp_path / "source.csv"
    sample.write_bytes(b"year,value\n1950,5\n")
    reviews = [
        {
            "report": "synthetic.json",
            "evidence": [
                {
                    "file": "source.csv",
                    "sha256": "wrong-pin",
                    "url": "https://example.test/source.csv",
                }
            ],
        }
    ]
    checks, attention = _evidence_checks(reviews, tmp_path, hash_files=True)
    file_check = next(item for item in checks if item.get("file") == "source.csv")
    url_check = next(item for item in checks if item.get("url"))
    assert file_check["status"] == "hash_mismatch"
    assert file_check["reported_original_pin"] == "wrong-pin"
    assert "observed_current_hash" in file_check
    assert url_check == {
        "report": "synthetic.json",
        "url": "https://example.test/source.csv",
        "status": "not_archived_url",
    }
    assert attention == [
        {
            "report": "synthetic.json",
            "url": "https://example.test/source.csv",
            "kind": "unarchived_web_url",
        }
    ]


def test_evidence_without_reported_pin_is_labeled_consolidation_time(
    tmp_path: Path,
) -> None:
    sample = tmp_path / "source.csv"
    sample.write_bytes(b"year,value\n1950,5\n")
    reviews = [{"report": "synthetic.json", "evidence": [{"file": "source.csv"}]}]
    checks, attention = _evidence_checks(reviews, tmp_path, hash_files=True)
    assert not attention
    assert checks == [
        {
            "report": "synthetic.json",
            "file": "source.csv",
            "status": "observed_current_hash",
            "observed_current_hash": (
                "f390df17fe67eae5bb79e52e855adece0a12115af1aa75fa574b6392ff554386"
            ),
            "hash_origin": "consolidation_time",
            "reported_original_pin": None,
        }
    ]


def test_evidence_path_review_flags_unsafe_and_url_without_opening_files(
    tmp_path: Path,
) -> None:
    reviews = [
        {
            "report": "synthetic.json",
            "evidence": [
                {"file": "../api.env"},
                {"url": "https://example.test/unarchived.pdf"},
            ],
        }
    ]
    checks, attention = _evidence_checks(reviews, tmp_path)
    assert {item["status"] for item in checks} == {"unsafe_path", "not_archived_url"}
    assert {item["kind"] for item in attention} == {
        "unsafe_evidence_path",
        "unarchived_web_url",
    }
