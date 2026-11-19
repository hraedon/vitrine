"""The auxiliary report covers every room and must not certify source accuracy."""

from pathlib import Path

import pytest
from cross_check import (
    check_note_source_mismatch,
    check_quantity_in_value,
    check_source_resolves,
    check_tier_discipline,
    load_facts,
    main,
)


def _room(data: Path, country: str) -> None:
    path = data / country
    path.mkdir()
    (path / "1950s.toml").write_text(
        f'[room]\ncountry = "{country}"\ndecade = "1950s"\n'
        f'[[fact]]\nid = "{country}-1950s-x"\nsource = "s"\n'
        'value = "21%"\nquantity = 1\ntier = "A"\n', encoding="utf-8",
    )


def test_room_discovery_includes_all_countries_and_excludes_series(tmp_path: Path) -> None:
    for country in ("us", "uk", "jp", "new"):
        _room(tmp_path, country)
    series = tmp_path / "series"
    series.mkdir()
    (series / "series.toml").write_text('[[series]]\nid = "not-a-fact"\n', encoding="utf-8")
    assert {fact["_country"] for fact in load_facts(tmp_path)} == {"us", "uk", "jp", "new"}
    assert len(check_quantity_in_value(load_facts(tmp_path))) == 4


@pytest.mark.parametrize("quantity,value", [(1, "21%"), (5, "-5%"), (float("nan"), "NaN")])
def test_wrong_numeric_tokens_fail_instead_of_passing_a_duplicate_substring_gate(
    quantity: float, value: str,
) -> None:
    assert check_quantity_in_value([{"id": "x", "quantity": quantity, "value": value}])


def test_complete_numeric_tokens_keep_core_precision_controls() -> None:
    assert not check_quantity_in_value([
        {"quantity": 12.3, "value": "12.300%"},
        {"quantity": 1234, "value": "1,234"},
    ])


def test_documented_gaps_do_not_recommend_upgrading_a_confidence_tier() -> None:
    issues = check_tier_discipline([
        {"id": "gap", "tier": "D", "value": "no reliable record transcribed here"},
        {"id": "estimate", "tier": "D", "value": "estimate from scholarship"},
    ])
    assert len(issues) == 1 and "estimate" in issues[0] and "gap" not in issues[0]


def test_generic_publisher_mention_matches_the_actual_source_registration() -> None:
    source = {"id": "nchs-db548", "publisher": "NCHS", "title": "Vital Statistics"}
    assert not check_note_source_mismatch(
        [{"id": "x", "source": source["id"], "notes": "From NCHS table."}],
        {source["id"]: source},
    )


def test_missing_source_is_a_structural_failure_even_when_empty() -> None:
    assert check_source_resolves([{"id": "x", "source": "", "_file": "room.toml"}], {})


def test_report_does_not_claim_to_verify_unread_sources(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    _room(tmp_path, "jp")
    (tmp_path / "sources.toml").write_text(
        '[[source]]\nid = "s"\nurl = "https://example.org/source"\n', encoding="utf-8",
    )
    assert main(["--data", str(tmp_path)]) == 1  # wrong quantity token in this room
    output = capsys.readouterr().out
    assert "Facts checked: 1" in output
    path = tmp_path / "jp" / "1950s.toml"
    path.write_text(path.read_text(encoding="utf-8").replace("quantity = 1", "quantity = 21"),
                    encoding="utf-8")
    assert main(["--data", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "Source values were not re-extracted" in output
    assert "zero miscites" not in output
