"""Adversarial synthetic cases for household/person record handling.

These tests use invented rows only. They never read the archived extract.
"""

from __future__ import annotations

import ipums_family_income_1950 as curator
from test_ipums_family_income_1950 import reader, row, rows_for_release


def primary_heads(rows):
    return [record for record in rows if record["PERNUM"] == "1"]


def complete_primary_units(heads):
    """Add three synthetic primary-family members to each selected head."""
    members = []
    for head in heads:
        serial = int(head["SERIAL"])
        for pernum in range(2, 5):
            members.append(
                row(
                    serial,
                    PERNUM=pernum,
                    RELATE=2,
                    GQ=head["GQ"],
                    FAMUNIT=1,
                    FAMSIZE=4,
                    metro=int(head["METRO"]),
                    income=10000,
                    weight="0",
                )
            )
    return members


def test_only_one_eligible_household_head_contributes_per_household() -> None:
    rows = rows_for_release()
    heads = primary_heads(rows)
    secondary_members = []
    for head in heads:
        serial = int(head["SERIAL"])
        # A conflicting secondary family must not alter the primary-family
        # head's income observation or the FAMUNIT=1 member-count check.
        secondary_members.append(
            row(
                serial,
                PERNUM=5,
                RELATE=2,
                FAMUNIT=2,
                income=-1,
                weight="330.00",
            )
        )

    base = curator.aggregate(
        reader(rows), tuple(sorted(curator.REQUIRED))
    )
    expanded = curator.aggregate(
        reader([*rows, *secondary_members]), tuple(sorted(curator.REQUIRED))
    )

    assert expanded == base
    assert expanded["groups"]["nonmetro"]["unweighted_count"] == 30


def test_period_household_selection_excludes_gq_2_units() -> None:
    rows = rows_for_release()
    heads = primary_heads(rows)
    # Keep at least 30 eligible nonmetro families after excluding this case.
    extra_head = row(999999, metro=1)
    heads.append(extra_head)
    rows.extend([extra_head, *complete_primary_units([extra_head])])
    excluded_serial = next(head["SERIAL"] for head in heads if head["METRO"] == "1")
    for record in rows:
        if record["SERIAL"] == excluded_serial:
            record["GQ"] = "2"

    result = curator.aggregate(reader(rows), tuple(sorted(curator.REQUIRED)))

    assert result["groups"]["nonmetro"]["unweighted_count"] == 30


def test_four_person_filter_checks_actual_primary_unit_members() -> None:
    rows = rows_for_release()
    malformed_serial = primary_heads(rows)[0]["SERIAL"]
    extra_head = row(999998, metro=1)
    rows.extend([extra_head, *complete_primary_units([extra_head])])
    source = [
        record
        for record in rows
        if not (record["SERIAL"] == malformed_serial and record["PERNUM"] == "4")
    ]

    result = curator.aggregate(reader(source), tuple(sorted(curator.REQUIRED)))

    # The one person claiming FAMSIZE=4 but having only three recorded primary
    # family members must be excluded and recorded in the mismatch diagnostic.
    assert result["counts"]["primary_unit_size_mismatch"] is None
    assert "primary_unit_size_mismatch" in result["suppressed_counts"]
    assert result["groups"]["nonmetro"]["unweighted_count"] == 30


def test_single_net_loss_does_not_block_headline_medians() -> None:
    source = rows_for_release()
    next(head for head in primary_heads(source) if head["METRO"] == "1")["FTOTINC"] = "-1"

    result = curator.aggregate(reader(source), tuple(sorted(curator.REQUIRED)))

    assert result["groups"]["nonmetro"]["unweighted_count"] == 30
    assert result["counts"]["net_loss_code"] is None
    assert "net_loss_code" in result["suppressed_counts"]
