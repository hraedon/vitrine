"""Literal food categories remain separate from the withdrawn denominator comparison."""

from pathlib import Path

import pytest
from cex_1972_review import FILE, extract, qualify, selected_amount, selected_row


def test_original_1972_food_rows_reproduce_placard() -> None:
    root = Path(__file__).parent.parent
    if not (root / "samples" / FILE).is_file():
        pytest.skip("original gitignored 1972-73 CEX report required")
    pytest.importorskip("pypdf", reason="curator-only PDF reader required")
    qualify(root / "samples", root / "data")


def test_changed_1972_report_cannot_reuse_the_inspected_vintage() -> None:
    with pytest.raises(ValueError, match="original 1972-73 CEX source changed"):
        extract(b"different report")


def test_unselected_damaged_token_does_not_shift_selection() -> None:
    row = "103.58 40.77 84.53 110.73 139.02 J.67 .73 202.81"
    assert selected_amount(row, 0) == "139.02"
    with pytest.raises(ValueError, match="selected column"):
        selected_amount(row.replace("139.02", "139 .02"), 0)
    with pytest.raises(ValueError, match="selected column"):
        selected_amount(row.replace("84.53", "84 .53"), 0)


def test_row_boundary_does_not_skip_a_damaged_first_cell() -> None:
    row = "Food, total ... 1,595.57 773.45 1,377.93 1,760.73 2,088.85 2,336.38 2,704.69"
    assert selected_row(row) == ("foodtotal", "2088.85")
    with pytest.raises(ValueError, match="selected column"):
        selected_row(row.replace("1,595.57", "1,595 .57"))
