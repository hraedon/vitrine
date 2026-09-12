"""Exercise the shipped lead locators against synthetic source-shaped HTML.

This miniature table is a test fixture, not archived publisher evidence. The
real facts supply the audit references; independent fixture labels and cells
make a missing guard or incorrect column selection observable without samples/.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from vitrine.audit import check_audits, run_audit
from vitrine.loader import load_corpus
from vitrine.model import Corpus

DATA = Path(__file__).parent.parent / "data"
SOURCE = "childstats-phy4a-blood-lead"
SAMPLE = "48-blood-lead/childstats-phy4a-lead-table.html"
TITLE = (
    "PHY4.A  Lead in the blood of children: Selected blood lead levels of children "
    "ages 1&ndash;5, selected years 1976&ndash;1980 through 2017&ndash;March 2020"
)
OBSERVATIONS = (
    ("us-1970s-blood-lead-median-1976-1980", "1976&ndash;1980", "15.0"),
    ("us-1980s-blood-lead-median-1988-1994", "1988&ndash;1994", "3.0"),
    ("us-1990s-blood-lead-median-1999-2002", "1999&ndash;2002", "1.9"),
    ("us-2000s-blood-lead-median-2003-2006", "2003&ndash;2006", "1.6"),
    ("us-2000s-blood-lead-median-2007-2010", "2007&ndash;2010", "1.3"),
    ("us-2010s-blood-lead-median-2013-2016", "2013&ndash;2016", "0.7"),
    ("us-2010s-blood-lead-median-2017-2020", "2017&ndash;March 2020", "0.6"),
)


def _header(period: str) -> str:
    content = period
    if period == "2017&ndash;March 2020":
        content = f'<nobr/>{period}<sup><a href="#a">a</a></sup>'
    return f'<th scope="col">{content}</th>'


def _source_html() -> str:
    headings = "\n".join(_header(period) for _, period, _ in OBSERVATIONS)
    cells = "\n".join(f"<td>{value}</td>" for _, _, value in OBSERVATIONS)
    return (
        f"<h1>{TITLE}</h1>\n<table><thead><tr>\n"
        '<th scope="col" class="mainheadl">Characteristic</th>\n'
        f"{headings}\n</tr></thead><tbody>\n"
        '<tr><td scope="row">Arithmetic mean (&micro;g/dL)</td>'
        + "<td>99.9</td>" * 7
        + '</tr>\n<tr><td scope="row">50th percentile (&micro;g/dL)</td>\n'
        + cells
        + '\n</tr></tbody><tfoot><tr><td scope="row" colspan="8">'
        'SOURCE:  National Center for Health Statistics, NHANES</td></tr>'
        "</tfoot></table>\n"
    )


@pytest.fixture(scope="module")
def lead_corpus() -> Corpus:
    corpus = load_corpus(DATA)
    rooms = tuple(
        replace(room, facts=tuple(fact for fact in room.facts if fact.source == SOURCE))
        for room in corpus.rooms
        if any(fact.source == SOURCE for fact in room.facts)
    )
    assert {fact.id for room in rooms for fact in room.facts} == {
        fact_id for fact_id, _, _ in OBSERVATIONS
    }
    # The synthetic bytes deliberately have no relationship to production pins.
    return replace(corpus, rooms=rooms, audit_ledger=())


def _sample(tmp_path: Path, content: str) -> None:
    sample = tmp_path / SAMPLE
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_text(content, encoding="utf-8")


def _reject_changed_source(corpus: Corpus, tmp_path: Path, changed: str) -> list[str]:
    original = _source_html()
    assert changed != original
    _sample(tmp_path, original)
    entries, errors = run_audit(corpus, tmp_path)
    assert errors == []
    assert len(entries) == 7
    _sample(tmp_path, changed)
    rejected, errors = run_audit(
        replace(corpus, audit_ledger=entries), tmp_path, accept_changed_samples=True,
    )
    # Explicit repinning bypasses the hash check, so rejection must come from
    # the actual extraction/context checks, and no partial ledger may escape.
    assert rejected == ()
    assert errors
    assert all("sample hash changed" not in error for error in errors)
    return errors


def test_shipped_lead_audits_extract_all_seven_fields(lead_corpus: Corpus, tmp_path: Path) -> None:
    _sample(tmp_path, _source_html())
    entries, errors = run_audit(lead_corpus, tmp_path)
    assert errors == []
    assert {entry.fact_id: entry.extracted for entry in entries} == {
        fact_id: value for fact_id, _, value in OBSERVATIONS
    }
    assert check_audits(replace(lead_corpus, audit_ledger=entries)) == []


@pytest.mark.parametrize("before,after", [
    ("children ages 1&ndash;5", "children ages 6&ndash;11"),
    ("50th percentile", "Geometric mean"),
    ("50th percentile (&micro;g/dL)", "50th percentile (mg/dL)"),
    ("National Center for Health Statistics", "Different Statistical Agency"),
], ids=["age", "statistic", "unit", "source-agency"])
def test_changed_source_meaning_rejected_even_when_repinning(
    lead_corpus: Corpus, tmp_path: Path, before: str, after: str,
) -> None:
    errors = _reject_changed_source(
        lead_corpus, tmp_path, _source_html().replace(before, after),
    )
    assert len(errors) == 7


@pytest.mark.parametrize("fact_id,period,value", OBSERVATIONS)
def test_each_numeric_cell_is_bound_to_its_fact(
    lead_corpus: Corpus, tmp_path: Path, fact_id: str, period: str, value: str,
) -> None:
    changed = _source_html().replace(f"<td>{value}</td>", "<td>42.42</td>")
    errors = _reject_changed_source(lead_corpus, tmp_path, changed)
    assert len(errors) == 1
    assert errors[0].startswith(fact_id + ":") and "MISMATCH" in errors[0]


@pytest.mark.parametrize("fact_id,period,value", OBSERVATIONS)
def test_each_column_requires_its_declared_survey_period(
    lead_corpus: Corpus, tmp_path: Path, fact_id: str, period: str, value: str,
) -> None:
    changed = _source_html().replace(_header(period), _header("DIFFERENT-PERIOD"))
    errors = _reject_changed_source(lead_corpus, tmp_path, changed)
    assert len(errors) == 1
    assert errors[0].startswith(fact_id + ":") and "source context changed" in errors[0]


def test_reordered_periods_cannot_relabel_unchanged_numbers(
    lead_corpus: Corpus, tmp_path: Path,
) -> None:
    first, second = (_header(OBSERVATIONS[i][1]) for i in (0, 1))
    changed = _source_html().replace(first, "TEMP").replace(second, first).replace("TEMP", second)
    errors = _reject_changed_source(lead_corpus, tmp_path, changed)
    assert {error.split(":", 1)[0] for error in errors} == {
        OBSERVATIONS[0][0], OBSERVATIONS[1][0],
    }


def test_inserted_period_cannot_shift_the_meaning_of_every_column(
    lead_corpus: Corpus, tmp_path: Path,
) -> None:
    changed = _source_html().replace(
        ">Characteristic</th>", ">Characteristic</th>" + _header("EXTRA-PERIOD"),
    )
    assert len(_reject_changed_source(lead_corpus, tmp_path, changed)) == 7
