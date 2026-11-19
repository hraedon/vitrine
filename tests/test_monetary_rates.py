"""Rates retain subminor precision without losing currency or time semantics."""

from dataclasses import replace
from pathlib import Path

import pytest

from vitrine.check import check_corpus, check_series
from vitrine.derive import DeriveError, evaluate
from vitrine.export import corpus_payload
from vitrine.model import (
    Basis,
    Corpus,
    DerivedFact,
    DerivedOp,
    Fact,
    Panel,
    Room,
    SeriesKind,
    Source,
    Tier,
)
from vitrine.series import Series, SeriesError, load_series, representation_problems
from vitrine.site.curation import Metric
from vitrine.site.projections.metrics import resolve_metric, series_numeric

DATA = Path(__file__).parent.parent / "data"


def rate(currency: str = "USD", basis: Basis = Basis.HOURLY) -> Series:
    return Series(
        id="rate", label="Rate", source="source", tier=Tier.A, unit="earnings",
        population="workers", values={1950: 1.3158, 1960: 2.5001},
        currency=currency, rate_basis=basis,
    )


def corpus(facts: tuple[Fact, ...] = (), derived: tuple[DerivedFact, ...] = ()) -> Corpus:
    return Corpus(
        sources={"source": Source("source", "Source", "Publisher", 1950,
                                  "https://example.org", "workers")},
        assumptions={}, rooms=(Room("us", "1950s", facts, derived),),
    )


def write_series(tmp_path: Path, metadata: str) -> Path:
    directory = tmp_path / "series"
    directory.mkdir()
    path = directory / "rate.toml"
    path.write_text(
        '[[series]]\nid = "rate"\nlabel = "Rate"\nsource = "source"\n'
        'tier = "A"\nunit = "earnings"\npopulation = "workers"\n'
        + metadata, encoding="utf-8",
    )
    return tmp_path


@pytest.mark.parametrize("basis", ["hourly", "weekly", "monthly", "annual"])
def test_explicit_rates_load_without_rounding(tmp_path: Path, basis: str) -> None:
    write_series(tmp_path, 'kind = "monetary_rate"\ncurrency = "JPY"\n'
                 f'rate_basis = "{basis}"\n[series.values]\n1950 = 1.3158\n')
    loaded = load_series(tmp_path)["rate"]
    assert loaded.kind is SeriesKind.MONETARY_RATE
    assert loaded.rate_basis is Basis(basis)
    assert loaded.currency == "JPY" and loaded.values == {1950: 1.3158}
    assert series_numeric(loaded) == {1950: 1.3158}


@pytest.mark.parametrize("metadata, diagnostic", [
    ('kind = "monetary_rate"\ncurrency = "USD"\n', "requires a valid rate_basis"),
    ('kind = "monetary_rate"\nrate_basis = "hourly"\n', "must declare currency"),
    ('kind = "monetary_rate"\ncurrency = "USD"\nrate_basis = "total"\n', "cannot be total"),
    ('currency = "USD"\n', "non-monetary"),
    ('rate_basis = "hourly"\n', "requires kind"),
    ('kind = "price"\n', "unknown series kind"),
    ('kind = "monetary_amount"\ncurrency = "USD"\n', "disagrees"),
])
def test_ambiguous_float_money_is_rejected(tmp_path: Path, metadata: str, diagnostic: str) -> None:
    write_series(tmp_path, metadata + "[series.values]\n1950 = 1.3158\n")
    with pytest.raises(SeriesError, match=diagnostic):
        load_series(tmp_path)


def test_rates_cannot_use_minor_storage(tmp_path: Path) -> None:
    write_series(tmp_path, 'kind = "monetary_rate"\ncurrency = "USD"\n'
                 'rate_basis = "hourly"\n[series.values_minor]\n1950 = 132\n')
    with pytest.raises(SeriesError, match="must use values"):
        load_series(tmp_path)


@pytest.mark.parametrize("table, metadata", [
    ("values", ""), ("values_minor", 'currency = "USD"\n'),
])
def test_numeric_year_aliases_cannot_overwrite_an_observation(
    tmp_path: Path, table: str, metadata: str,
) -> None:
    write_series(tmp_path, metadata + f"[series.{table}]\n1950 = 1\n01950 = 2\n")
    with pytest.raises(SeriesError, match="duplicate numeric year 1950"):
        load_series(tmp_path)


@pytest.mark.parametrize("candidate, diagnostic", [
    (replace(rate(), currency=""), "must declare currency"),
    (rate("XYZ"), "unknown currency"),
    (rate(basis=Basis.TOTAL), "rate_basis"),
    (replace(rate(), rate_basis=None), "non-monetary"),
    (replace(rate(), values_minor={1950: 132}), "exactly one"),
    (replace(rate(), values={}, values_minor={1950: 132}), "not values_minor"),
])
def test_programmatic_series_cannot_bypass_representation_gate(
    candidate: Series, diagnostic: str,
) -> None:
    assert any(diagnostic in p for p in check_series({candidate.id: candidate}, corpus()))
    with pytest.raises(ValueError):
        series_numeric(candidate)


def test_rates_reject_currency_and_basis_changes_in_annual_chains() -> None:
    price = Series("price", "Price", "source", Tier.A, "USD", "goods",
                   values_minor={1950: 10000}, currency="USD")
    metric = Metric("hours", "Hours", "hours", "caption",
                    numerator=("price",), denominator=("rate",))
    assert resolve_metric(metric, {"price": price, "rate": rate()})[0][1950] == pytest.approx(
        100 / 1.3158,
    )
    with pytest.raises(ValueError, match="currency mismatch"):
        resolve_metric(metric, {"price": price, "rate": rate("GBP")})
    other = replace(rate(basis=Basis.WEEKLY), id="weekly", values={1970: 55.01})
    with pytest.raises(ValueError, match="rate_basis"):
        resolve_metric(replace(metric, denominator=("rate", "weekly")),
                       {"price": price, "rate": rate(), "weekly": other})


@pytest.mark.parametrize("operation", [DerivedOp.INFLATE, DerivedOp.COUNT_ABOVE])
def test_rates_are_neither_inflation_indexes_nor_countable_quantities(operation: DerivedOp) -> None:
    fact = Fact("us-1950s-price", Panel.WORK_BUYS, "Price", "$10", "USD", "source", Tier.A,
                amount_minor=1000, currency="USD", price_year=1950, basis=Basis.ANNUAL)
    derived = DerivedFact(
        "us-1950s-derived", Panel.WORK_BUYS, "Derived", "result", operation,
        numerator=fact.id if operation is DerivedOp.INFLATE else "",
        inflate_series="rate", inflate_from_year=1950, inflate_to_year=1960,
        count_series=("rate",), at_year=1950, threshold=1,
    )
    museum = corpus((fact,), (derived,))
    assert any("monetary" in p for p in check_corpus(museum, {"rate": rate()}))
    with pytest.raises(DeriveError, match="non-monetary"):
        evaluate(museum.rooms[0], derived, {"rate": rate()})


@pytest.mark.parametrize("currency, basis, amount, value", [
    ("USD", Basis.HOURLY, 132, 1.3158),
    ("GBP", Basis.WEEKLY, 5329, 53.2911),
    ("JPY", Basis.MONTHLY, 29169, 29169.4),
])
def test_rate_drift_uses_currency_scale_and_matching_time_basis(
    currency: str, basis: Basis, amount: int, value: float,
) -> None:
    fact = Fact("us-1950s-earnings", Panel.DAY, "Earnings", "shown", "earnings", "source", Tier.A,
                amount_minor=amount, currency=currency, price_year=1950, basis=basis)
    candidate = replace(rate(currency, basis), values={1950: value})
    assert check_series({"rate": candidate}, corpus((fact,))) == []
    drift = replace(candidate, values={1950: value + 10})
    assert any("drifted" in p for p in check_series({"rate": drift}, corpus((fact,))))
    wrong_basis = replace(candidate, rate_basis=Basis.ANNUAL)
    assert check_series({"rate": wrong_basis}, corpus((fact,))) == []
    wrong_currency = replace(candidate, currency="GBP" if currency != "GBP" else "USD")
    assert any("currency mismatch" in p
               for p in check_series({"rate": wrong_currency}, corpus((fact,))))


def test_rate_splice_requires_same_currency_and_time_basis() -> None:
    first = rate()
    for second in (rate("GBP"), rate(basis=Basis.WEEKLY)):
        second = replace(second, id="next", splices_from="rate", values={1970: 55.01})
        assert check_series({"rate": first, "next": second}, corpus())
    second = replace(first, id="next", splices_from="rate", values={1970: 55.01})
    assert check_series({"rate": first, "next": second}, corpus()) == []


def test_equal_minor_unit_numerals_do_not_hide_a_fact_series_currency_mismatch() -> None:
    fact = Fact(
        "us-1950s-amount", Panel.BUDGET, "Amount", "£1", "GBP", "source", Tier.A,
        amount_minor=100, currency="GBP", price_year=1950, basis=Basis.ANNUAL,
    )
    candidate = Series("amount", "Amount", "source", Tier.A, "USD", "population",
                       values_minor={1950: 100}, currency="USD")
    assert any("currency mismatch" in p
               for p in check_series({"amount": candidate}, corpus((fact,))))
    assert check_series({"amount": replace(candidate, currency="GBP")}, corpus((fact,))) == []


def test_export_v2_makes_rate_representation_reproducible() -> None:
    payload = corpus_payload(corpus(), {"rate": rate()})
    assert payload["schema_version"] == 2
    exported = payload["series"][0]
    assert exported["kind"] == "monetary_rate" and exported["rate_basis"] == "hourly"
    assert exported["currency"] == "USD" and exported["values"]["1950"] == 1.3158
    assert exported["values_minor"] == {}


def test_committed_earnings_all_declare_rates_and_preserve_subcent_values() -> None:
    series = load_series(DATA)
    earnings = [s for s in series.values() if s.kind is SeriesKind.MONETARY_RATE]
    assert {s.id for s in earnings} == {
        "hourly-earnings-manufacturing", "hourly-earnings-total-private",
        "weekly-earnings-manufacturing",
    }
    assert all(s.currency == "USD" and not representation_problems(s) for s in earnings)
    assert all(any(abs(value * 100 - round(value * 100)) > 1e-6 for value in s.values.values())
               for s in earnings)
