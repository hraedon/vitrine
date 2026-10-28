"""Historical cause-specific rates bind directly to original CDC aggregate CSV rows."""

import csv
import hashlib
import io
from dataclasses import replace
from pathlib import Path

import pytest

from vitrine.audit import run_audit
from vitrine.loader import load_corpus
from vitrine.model import Corpus, Fact

ROOT = Path(__file__).parent.parent
SHA256 = "867d39e039b9ecb9843be3e8b3473250fec03050dc62d7d4409c1f737b731160"
FILE = f"60-mortality-review/nchs-cause-mortality-6rkc-nb2q-{SHA256}.csv"


def selected() -> Corpus:
    full = load_corpus(ROOT / "data")
    rooms = tuple(
        replace(room, facts=tuple(f for f in room.facts if f.source == "nchs-mortality-trends"),
                derived=())
        for room in full.rooms
        if any(f.source == "nchs-mortality-trends" for f in room.facts)
    )
    return replace(full, rooms=rooms, audit_ledger=())


def test_every_existing_historical_cause_rate_has_year_and_cause_guards() -> None:
    facts = [fact for room in selected().rooms for fact in room.facts]
    assert len(facts) == 15
    for fact in facts:
        assert fact.audit and fact.audit.file == FILE
        guards = {guard.locator: guard.value for guard in fact.audit.guards}
        row = fact.audit.locator.split(":")[0]
        assert guards["R1:C1"] == "Year" and guards["R1:C2"] == "Cause"
        assert guards["R1:C3"] == "Age Adjusted Death Rate"
        assert guards[f"{row}:C1"] in fact.label
        assert guards[f"{row}:C2"] in {"Heart Disease", "Cancer", "Stroke"}


def test_original_cdc_csv_reproduces_all_fifteen_historical_rates() -> None:
    path = ROOT / "samples" / FILE
    if not path.is_file():
        pytest.skip("gitignored original CDC aggregate CSV required")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == SHA256
    entries, errors = run_audit(selected(), ROOT / "samples")
    assert not errors and len(entries) == 15
    assert all(entry.sample_sha256 == SHA256 for entry in entries)


@pytest.mark.parametrize("change", ["year", "cause", "header"])
def test_same_numeric_rate_cannot_reuse_wrong_row_context(tmp_path: Path, change: str) -> None:
    path = ROOT / "samples" / FILE
    if not path.is_file():
        pytest.skip("gitignored original CDC aggregate CSV required")
    museum = selected()
    room = next(room for room in museum.rooms if room.slug == "us-1950s")
    fact: Fact = next(f for f in room.facts if f.id == "us-1950s-heart-disease-mortality")
    assert fact.audit
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
    row_number = int(fact.audit.locator.split(":")[0][1:]) - 1
    if change == "header":
        rows[0][2] = "Crude Death Rate"
    else:
        rows[row_number][0 if change == "year" else 1] = "1951" if change == "year" else "Cancer"
    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\n").writerows(rows)
    changed = tmp_path / FILE
    changed.parent.mkdir(parents=True)
    changed.write_text(output.getvalue(), encoding="utf-8")
    specimen = replace(museum, rooms=(replace(room, facts=(fact,)),))
    entries, errors = run_audit(specimen, tmp_path)
    assert not entries and any("source context changed" in error for error in errors)
