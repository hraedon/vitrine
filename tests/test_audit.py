"""Transcription, evidence identity, and failure-preserving publication checks."""

from dataclasses import replace
from pathlib import Path

import pytest

from vitrine.audit import (
    check_audits,
    coverage_report,
    decimal_value,
    load_ledger,
    parse_ref,
    run_audit,
    write_ledger,
)
from vitrine.model import (
    AuditGuard,
    AuditRef,
    AuditTarget,
    Corpus,
    Extractor,
    Fact,
    Panel,
    Room,
    Source,
    Tier,
)


def specimen(ref: AuditRef, **changes: object) -> Corpus:
    fact = Fact(
        "us-1950s-test",
        Panel.BUDGET,
        "Annual earnings, 1950",
        "$12.34",
        "USD",
        "s",
        Tier.A,
        quantity=12.34,
        audit=ref,
    )
    fact = replace(fact, **changes)
    return Corpus(
        sources={
            "s": Source(
                "s",
                "Source table",
                "Publisher",
                1950,
                "https://example.org/table",
                "Survey workers",
            )
        },
        assumptions={},
        rooms=(Room("us", "1950s", (fact,)),),
    )


def csv_ref() -> AuditRef:
    return AuditRef(
        "table.csv",
        Extractor.CSV_CELL,
        "R2:C2",
        guards=(AuditGuard("R1:C2", "Earnings"), AuditGuard("R2:C1", "1950")),
    )


def test_csv_guarded_audit_and_deterministic_ledger(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_text('Year,Earnings\n1950,"$12.34"\n', encoding="utf-8")
    corpus = specimen(csv_ref())
    entries, errors = run_audit(corpus, tmp_path, audited="2026-09-07")
    assert not errors and len(entries) == 1
    ledger = tmp_path / "audit-ledger.toml"
    write_ledger(ledger, entries)
    first = ledger.read_bytes()
    write_ledger(ledger, run_audit(corpus, tmp_path, audited="2026-09-07")[0])
    assert ledger.read_bytes() == first
    audited = replace(corpus, audit_ledger=load_ledger(ledger))
    assert check_audits(audited) == []
    assert "1 current" in coverage_report(audited)


@pytest.mark.parametrize(
    "field,value",
    [
        ("value", "$12.340"),
        ("quantity", 99.0),
        ("label", "Different statistic"),
        ("unit", "JPY"),
        ("notes", "Changed interpretation"),
        ("tier", Tier.C),
        ("audit", replace(csv_ref(), extractor=Extractor.TEXT_REGEX, locator=r"(12\.34)")),
    ],
)
def test_fact_semantics_drift_invalidates_ledger(tmp_path: Path, field: str, value: object) -> None:
    (tmp_path / "table.csv").write_text("Year,Earnings\n1950,12.34\n")
    corpus = specimen(csv_ref())
    entries, _ = run_audit(corpus, tmp_path)
    fact = replace(corpus.rooms[0].facts[0], **{field: value})
    changed = replace(
        corpus, rooms=(replace(corpus.rooms[0], facts=(fact,)),), audit_ledger=entries
    )
    assert any("stale" in error for error in check_audits(changed))


def test_source_population_drift_invalidates_ledger(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_text("Year,Earnings\n1950,12.34\n")
    corpus = specimen(csv_ref())
    entries, _ = run_audit(corpus, tmp_path)
    changed = replace(
        corpus,
        audit_ledger=entries,
        sources={"s": replace(corpus.sources["s"], population="All families")},
    )
    assert any("stale" in error for error in check_audits(changed))


def test_changed_archive_requires_explicit_repin_and_guards_still_apply(tmp_path: Path) -> None:
    sample = tmp_path / "table.csv"
    sample.write_text("Year,Earnings\n1950,12.34\n")
    corpus = specimen(csv_ref())
    entries, _ = run_audit(corpus, tmp_path)
    corpus = replace(corpus, audit_ledger=entries)
    sample.write_text("Year,Earnings\n1950,12.34\n1951,99\n")
    assert "sample hash changed" in run_audit(corpus, tmp_path)[1][0]
    assert not run_audit(corpus, tmp_path, accept_changed_samples=True)[1]
    sample.write_text("Year,Earnings\n1951,12.34\n")
    assert (
        "source context changed" in run_audit(corpus, tmp_path, accept_changed_samples=True)[1][0]
    )


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Year,Earnings\n1950,99\n", "MISMATCH"),
        ("Year,Other\n1950,12.34\n", "source context"),
        ("Year,Earnings\n", "parse-error"),
    ],
)
def test_failed_audit_returns_no_publishable_entries(
    tmp_path: Path, text: str, expected: str
) -> None:
    (tmp_path / "table.csv").write_text(text)
    entries, errors = run_audit(specimen(csv_ref()), tmp_path)
    assert entries == () and expected in errors[0] and "us-1950s-test" in errors[0]


def test_regex_requires_one_match_and_one_group(tmp_path: Path) -> None:
    ref = AuditRef("source.txt", Extractor.TEXT_REGEX, r"^1950: ([\d.]+)$")
    corpus = specimen(ref)
    (tmp_path / "source.txt").write_text("1950: 12.34\n1951: 7\n")
    assert not run_audit(corpus, tmp_path)[1]
    (tmp_path / "source.txt").write_text("1950: 12.34\n1950: 12.34\n")
    assert "exactly once" in run_audit(corpus, tmp_path)[1][0]
    with pytest.raises(ValueError, match="locator"):
        parse_ref({"file": "t", "extractor": "text-regex", "locator": "(1)(2)"})


def test_xlsx_literals_and_decimal_minor_unit_scaling(tmp_path: Path) -> None:
    import openpyxl

    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Earnings"
    sheet.append(["Year", "USD"])
    sheet.append([1950, 12.34])
    path = tmp_path / "table.xlsx"
    book.save(path)
    ref = AuditRef(
        "table.xlsx",
        Extractor.XLSX_CELL,
        "Earnings!B2",
        scale="100",
        target=AuditTarget.AMOUNT_MINOR,
        guards=(AuditGuard("Earnings!A2", "1950"),),
    )
    corpus = specimen(ref, amount_minor=1234)
    assert not run_audit(corpus, tmp_path)[1]
    sheet["B2"] = "=12.34"
    book.save(path)
    assert "formula cell" in run_audit(corpus, tmp_path)[1][0]
    book.close()


def test_cp932_csv_is_explicit_and_pinned_as_original_bytes(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_bytes("年,賃金\n1950,12.34\n".encode("cp932"))
    ref = replace(csv_ref(), encoding="cp932", guards=(AuditGuard("R1:C2", "賃金"),))
    assert not run_audit(specimen(ref), tmp_path)[1]
    assert run_audit(specimen(replace(ref, encoding="utf-8")), tmp_path)[1]


@pytest.mark.parametrize("path", ["../outside.csv", "/absolute.csv", "C:/a", "a\\b", "a/./b"])
def test_samples_paths_are_relative(path: str) -> None:
    with pytest.raises(ValueError, match="relative"):
        parse_ref({"file": path, "extractor": "csv-cell", "locator": "R1:C1"})


@pytest.mark.parametrize("value", ["nan", "inf", "12.3 note", "1,2", True, None, ""])
def test_numeric_canonicalization_rejects_ambiguous_cells(value: object) -> None:
    with pytest.raises(ValueError):
        decimal_value(value)


def test_removed_audited_fact_cannot_silently_disappear(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_text("Year,Earnings\n1950,12.34\n")
    corpus = specimen(csv_ref())
    entries, _ = run_audit(corpus, tmp_path)
    missing = replace(corpus, rooms=(), audit_ledger=entries)
    assert "no longer exists" in check_audits(missing)[0]
    assert "removed" in run_audit(missing, tmp_path)[1][0]


def test_duplicate_or_malformed_ledger_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "table.csv").write_text("Year,Earnings\n1950,12.34\n")
    entries, _ = run_audit(specimen(csv_ref()), tmp_path)
    path = tmp_path / "audit-ledger.toml"
    write_ledger(path, entries + entries)
    with pytest.raises(ValueError, match="duplicate"):
        load_ledger(path)
    path.write_text("version = 999\n")
    with pytest.raises(ValueError, match="version"):
        load_ledger(path)


def test_missing_ledger_cannot_turn_audited_facts_green() -> None:
    assert "no ledger entry" in check_audits(specimen(csv_ref()))[0]


def test_corrupt_workbook_reports_parse_error(tmp_path: Path) -> None:
    (tmp_path / "broken.xlsx").write_bytes(b"not a workbook")
    ref = AuditRef("broken.xlsx", Extractor.XLSX_CELL, "Sheet!A1")
    entries, errors = run_audit(specimen(ref), tmp_path)
    assert entries == () and "parse-error" in errors[0]


def test_cli_mismatch_preserves_ledger_bytes(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from vitrine.cli import main

    data = tmp_path / "data"
    data.mkdir()
    (data / "us").mkdir()
    (data / "sources.toml").write_text(
        "\n".join(
            [
                "[[source]]",
                'id = "s"',
                'title = "Sample"',
                'publisher = "Publisher"',
                "year = 1950",
                'url = "https://example.org/table"',
                'population = "Survey workers"',
            ]
        )
    )
    (data / "assumptions.toml").write_text("")
    (data / "us/1950s.toml").write_text(
        "\n".join(
            [
                "[room]",
                'country = "us"',
                'decade = "1950s"',
                "[[fact]]",
                'id = "us-1950s-test"',
                'panel = "budget"',
                'label = "Earnings"',
                'value = "12.34"',
                'unit = "USD"',
                'source = "s"',
                'tier = "A"',
                "quantity = 12.34",
                'audit = {file = "table.csv", extractor = "csv-cell", locator = "R2:C2"}',
            ]
        )
    )
    sample = tmp_path / "table.csv"
    sample.write_text("Year,Earnings\n1950,12.34\n")
    args = ["--data", str(data), "audit", "--samples", str(tmp_path)]
    assert main(args) == 0
    ledger = (data / "audit-ledger.toml").read_bytes()
    sample.write_text("Year,Earnings\n1950,99\n")
    assert main([*args, "--pin"]) == 1
    assert "MISMATCH" in capsys.readouterr().err
    assert (data / "audit-ledger.toml").read_bytes() == ledger
    assert main(["--data", str(data), "check"]) == 0  # offline bindings still match
