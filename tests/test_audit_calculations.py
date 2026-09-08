"""Replay arithmetic from original source operands, including context and rounding."""

import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from test_audit import specimen

from vitrine.audit import (
    calculate,
    check_audits,
    coverage_report,
    load_ledger,
    parse_ref,
    run_audit,
    write_ledger,
)
from vitrine.model import AuditCalculation, AuditOperation, AuditRef, AuditRounding, Extractor


def ratio_ref(rounding: str = "half_even") -> AuditRef:
    return parse_ref({
        "file": "spending.csv", "extractor": "csv-cell", "locator": "R2:C2",
        "guards": [
            {"locator": "R1:C2", "value": "All consumer units"},
            {"locator": "R2:C1", "value": "Food"},
            {"locator": "R3:C1", "value": "Total"},
        ],
        "calculation": {
            "op": "pct_of", "operands": ["R3:C2"], "precision": 1,
            "rounding": rounding, "method": "Food divided by total, same population; percent.",
        },
    })


def test_ratio_replays_raw_operands_and_detects_ledger_tampering(tmp_path: Path) -> None:
    (tmp_path / "spending.csv").write_text(
        "Item,All consumer units\nFood,5035\nTotal,23490\n", encoding="utf-8"
    )
    corpus = specimen(ratio_ref(), quantity=21.4)
    entries, errors = run_audit(corpus, tmp_path)
    assert not errors
    assert entries[0].operands == ("5035", "23490")
    assert entries[0].extracted == "21.4"
    ledger = tmp_path / "ledger.toml"
    write_ledger(ledger, entries)
    assert check_audits(replace(corpus, audit_ledger=load_ledger(ledger))) == []
    corrupt = replace(entries[0], operands=("5035", "25000"))
    assert "does not reproduce" in check_audits(replace(corpus, audit_ledger=(corrupt,)))[0]
    assert "0 current" in coverage_report(replace(corpus, audit_ledger=(corrupt,)))
    missing = replace(entries[0], operands=())
    assert "operand count" in check_audits(replace(corpus, audit_ledger=(missing,)))[0]


def test_rounding_is_explicit_and_exact_at_positive_and_negative_ties() -> None:
    even = ratio_ref()
    upward = ratio_ref("half_up")
    assert calculate(even, (Decimal("12.25"), Decimal(100))) == Decimal("12.2")
    assert calculate(upward, (Decimal("12.25"), Decimal(100))) == Decimal("12.3")
    assert calculate(upward, (Decimal("-12.25"), Decimal(100))) == Decimal("-12.3")
    with pytest.raises(ValueError, match="positive"):
        calculate(even, (Decimal(1), Decimal(0)))


def monthly_ref() -> AuditRef:
    base = "/Results/series/0"
    guards = [{"locator": base + "/seriesID", "value": "CES3000000008"}]
    for i in range(12):
        guards.extend([
            {"locator": f"{base}/data/{i}/year", "value": "1950"},
            {"locator": f"{base}/data/{i}/period", "value": f"M{i + 1:02d}"},
        ])
    return parse_ref({
        "file": "monthly.json", "extractor": "json-pointer", "locator": base + "/data/0/value",
        "scale": "100", "target": "amount_minor", "guards": guards,
        "calculation": {
            "op": "mean", "operands": [f"{base}/data/{i}/value" for i in range(1, 12)],
            "precision": 2, "rounding": "half_even",
            "method": "Arithmetic mean of twelve monthly earnings rates, January to December.",
        },
    })


def test_monthly_mean_requires_every_selected_month_and_exact_context(tmp_path: Path) -> None:
    rows = [{"year": "1950", "period": f"M{i+1:02d}", "value": "1.315"} for i in range(12)]
    document = {"Results": {"series": [{"seriesID": "CES3000000008", "data": rows}]}}
    source = tmp_path / "monthly.json"
    source.write_text(json.dumps(document))
    corpus = specimen(monthly_ref(), amount_minor=132)
    entries, errors = run_audit(corpus, tmp_path)
    assert not errors and entries[0].extracted == "1.32"
    assert len(entries[0].operands) == 12
    rows[11]["period"] = "M11"  # twelve rows can conceal a duplicate and missing month
    source.write_text(json.dumps(document))
    assert "source context changed" in run_audit(corpus, tmp_path)[1][0]
    rows.pop()
    source.write_text(json.dumps(document))
    assert run_audit(corpus, tmp_path)[0] == ()


@pytest.mark.parametrize("locator", ["/a/~2", "a/b"])
def test_json_pointer_requires_unambiguous_address(locator: str) -> None:
    with pytest.raises(ValueError, match="locator"):
        parse_ref({"file": "a.json", "extractor": "json-pointer", "locator": locator})


def test_json_pointer_escapes_and_no_composite_values(tmp_path: Path) -> None:
    source = tmp_path / "a.json"
    source.write_text(json.dumps({"a/b": {"~c": "12.34"}}))
    ref = AuditRef("a.json", Extractor.JSON_POINTER, "/a~1b/~0c")
    assert not run_audit(specimen(ref), tmp_path)[1]
    assert "scalar" in run_audit(specimen(replace(ref, locator="/a~1b")), tmp_path)[1][0]


def test_json_numeric_tokens_keep_precision_at_rounding_boundary(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text('{"a":1.24500000000000001,"b":1.24500000000000001}')
    calc = AuditCalculation(AuditOperation.MEAN, ("/b",), 2, AuditRounding.HALF_EVEN, "Mean")
    ref = AuditRef("a.json", Extractor.JSON_POINTER, "/a", calculation=calc)
    entries, errors = run_audit(specimen(ref, quantity=1.25), tmp_path)
    assert not errors
    assert entries[0].operands == ("1.24500000000000001", "1.24500000000000001")
    assert run_audit(specimen(ref, quantity=1.24), tmp_path)[0] == ()


def test_calculation_schema_rejects_implicit_or_duplicate_operands() -> None:
    raw = {"file": "t.csv", "extractor": "csv-cell", "locator": "R1:C1"}
    with pytest.raises(ValueError, match="requires"):
        parse_ref({**raw, "calculation": {"op": "mean"}})
    calc = AuditCalculation(AuditOperation.MEAN, ("R1:C1",), 2, AuditRounding.HALF_EVEN, "Mean")
    from vitrine.audit import validate_ref
    with pytest.raises(ValueError, match="distinct"):
        validate_ref(AuditRef("t.csv", Extractor.CSV_CELL, "R1:C1", calculation=calc))
