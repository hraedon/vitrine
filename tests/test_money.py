"""Tests for the money layer (plan 022 WI-1)."""
from __future__ import annotations

import pytest

from vitrine import money


def test_usd_format_is_byte_identical_to_the_old_hardcoded_path() -> None:
    # The invariant that lets the money layer land under the US corpus without
    # moving a rendered character: format_amount(x, "USD", p) == f"${x:,.{p}f}".
    for value in (0.0, 1.0, 12.5, 1234.5, 1234567.891):
        for precision in (0, 1, 2, 3):
            assert money.format_amount(value, "USD", precision) == f"${value:,.{precision}f}"


def test_gbp_formats_with_the_pound_symbol() -> None:
    assert money.format_amount(1234.5, "GBP", 2) == "£1,234.50"
    assert money.format_amount(0, "GBP", 0) == "£0"


def test_unknown_currency_raises_with_a_helpful_message() -> None:
    with pytest.raises(money.UnknownCurrency) as exc:
        money.get("XYZ")
    assert "XYZ" in str(exc.value)
    assert exc.value.code == "XYZ"
    assert not money.is_known("XYZ")
    assert money.is_known("USD") and money.is_known("GBP")


def test_format_amount_rejects_unknown_currency() -> None:
    with pytest.raises(money.UnknownCurrency):
        money.format_amount(1.0, "EUR", 2)


def test_format_minor_round_trips_the_minor_unit_scale() -> None:
    # Every registry entry: minor units display at the major scale.
    for code, cur in money.CURRENCIES.items():
        minor = 123456  # e.g. 1,234.56 for a 2-digit currency
        expected_major = minor / (10**cur.minor_digits)
        assert money.format_minor(minor, code) == money.format_amount(
            expected_major, code, cur.minor_digits
        )


def test_format_minor_default_precision_is_the_currencys_minor_digits() -> None:
    assert money.format_minor(100000, "USD") == "$1,000.00"
    assert money.format_minor(100000, "GBP") == "£1,000.00"


def test_separators_are_remapped_for_a_hypothetical_continental_currency() -> None:
    # Guard the _body separator-remap path against a currency that uses the
    # European "1.234,50" convention. Not yet in the registry; construct one.
    eur = money.Currency(
        "EUR", "€", symbol_before=False, minor_digits=2,
        group_sep=".", decimal_sep=",",
    )
    money.CURRENCIES["EUR"] = eur
    try:
        assert money.format_amount(1234.5, "EUR", 2) == "1.234,50 €"
    finally:
        del money.CURRENCIES["EUR"]
