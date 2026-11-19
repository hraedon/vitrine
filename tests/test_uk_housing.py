"""New housing observations preserve the publisher's population and errata."""

import hashlib
from pathlib import Path

import pytest
from uk_housing_extract import DEFAULT_ARCHIVE, FILES, _observation, extract

from vitrine.loader import load_corpus

DATA = Path(__file__).parent.parent / "data"


def test_housing_records_keep_dwelling_scope_and_do_not_erase_remaining_gap() -> None:
    corpus = load_corpus(DATA)
    room = next(room for room in corpus.rooms if room.slug == "uk-2010s")
    facts = {fact.id: fact for fact in room.facts}
    area = facts["uk-2010s-mean-dwelling-floor-area"]
    heating = facts["uk-2010s-dwelling-central-heating"]
    source = corpus.sources[area.source]
    assert area.quantity == 91 and "Mean" in area.label
    assert heating.quantity == 90 and "England" in heating.label
    assert "occupied or vacant" in source.population
    assert "April 2010 to March 2012" in source.population
    assert "integral balconies are included" in area.notes
    assert "electric storage heaters are excluded" in heating.notes
    assert facts["uk-2010s-housing-amenities-gap"].value.startswith("no reliable record")


def test_original_housing_pdfs_reproduce_audited_dump() -> None:
    report = DEFAULT_ARCHIVE / "ehs-homes-2011.pdf"
    errata = DEFAULT_ARCHIVE / "ehs-homes-2011-errata.pdf"
    dump = DEFAULT_ARCHIVE / "ehs-homes-2011-observations.txt"
    if not all(path.is_file() for path in (report, errata, dump)):
        pytest.skip("gitignored EHS original PDFs and extraction artifact required")
    for path in (report, errata):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == FILES[path.name][1]
    assert extract(report.read_bytes(), errata.read_bytes()) == dump.read_text(encoding="utf-8")


@pytest.mark.parametrize("text", ["missing", "value 90; value 91"])
def test_source_extraction_refuses_missing_or_conflicting_observations(text: str) -> None:
    with pytest.raises(ValueError, match="unambiguous"):
        _observation(text, r"value (\d+)")


def test_changed_report_cannot_reuse_the_inspected_source_pin() -> None:
    with pytest.raises(ValueError, match="publisher bytes differ"):
        extract(b"different source", b"different errata")
