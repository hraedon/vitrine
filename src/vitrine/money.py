"""The money layer — currency representation the world wing stands on.

A Fact declares a ``currency`` as an ISO 4217 code (``"USD"``, ``"GBP"``).
This module is the *closed registry* that (a) says a declared currency is one
the museum actually supports and (b) knows how to format an amount in it.
Adding a currency is one entry in ``CURRENCIES``.

Deliberately **no FX here, ever.** The museum never converts between
currencies as a truth-path number — cross-nation comparison is by
affordability, time-cost, and expenditure share, not by exchange rate (see
``plans/021`` and ``docs/fact-model.md``). This layer only *represents and
formats* amounts within a single currency.

Invariant that keeps the US corpus byte-identical while this layer lands: for
USD, ``format_amount(x, "USD", p)`` equals the old ``f"${x:,.{p}f}"`` exactly.
"""

from __future__ import annotations

from dataclasses import dataclass


class UnknownCurrency(Exception):
    """A fact (or derivation) declared a currency the registry doesn't know."""

    def __init__(self, code: str) -> None:
        super().__init__(
            f"unknown currency {code!r}; register it in vitrine.money.CURRENCIES"
        )
        self.code = code


@dataclass(frozen=True, slots=True)
class Currency:
    """How one currency is written. ``minor_digits`` is the number of minor
    units per major (2 = cents/pence). ``symbol_before`` places the symbol
    ahead of the number (``$1,234.50``) vs after it (``1 234,50 zł``)."""

    code: str  # ISO 4217, e.g. "USD"
    symbol: str  # "$", "£"
    symbol_before: bool
    minor_digits: int
    group_sep: str = ","
    decimal_sep: str = "."


# The closed registry. Seed: the two currencies plan 022/023 need. USD and GBP
# share Python's default separators and symbol-before placement, so seeding GBP
# alongside USD cannot perturb any existing US output.
CURRENCIES: dict[str, Currency] = {
    "USD": Currency("USD", "$", symbol_before=True, minor_digits=2),
    "GBP": Currency("GBP", "£", symbol_before=True, minor_digits=2),
}


def is_known(code: str) -> bool:
    """Whether ``code`` is a registered currency."""
    return code in CURRENCIES


def get(code: str) -> Currency:
    """Look up a registered currency, or raise :class:`UnknownCurrency`."""
    try:
        return CURRENCIES[code]
    except KeyError:
        raise UnknownCurrency(code) from None


def _body(number: str, cur: Currency) -> str:
    """Apply a currency's separators to a Python-formatted number string
    (which always uses ``,`` for groups and ``.`` for the decimal)."""
    if (cur.group_sep, cur.decimal_sep) == (",", "."):
        return number
    # Remap via a placeholder so the two swaps don't interfere.
    return (
        number.replace(",", "\0")
        .replace(".", cur.decimal_sep)
        .replace("\0", cur.group_sep)
    )


def format_amount(major: float, code: str, precision: int) -> str:
    """Format a *major-unit* amount (e.g. dollars) in ``code``.

    For USD this is byte-identical to ``f"${major:,.{precision}f}"`` — the
    property that lets the money layer land under the US corpus without moving
    a single rendered character.
    """
    cur = get(code)
    body = _body(f"{major:,.{precision}f}", cur)
    return f"{cur.symbol}{body}" if cur.symbol_before else f"{body} {cur.symbol}"


def format_minor(amount_minor: int, code: str, precision: int | None = None) -> str:
    """Format integer *minor* units (e.g. cents) in ``code``.

    ``precision`` defaults to the currency's ``minor_digits``. Minor units are
    the museum's drift-free integer storage for money; this is the display
    projection of them.
    """
    cur = get(code)
    digits = cur.minor_digits if precision is None else precision
    return format_amount(amount_minor / (10**cur.minor_digits), code, digits)
