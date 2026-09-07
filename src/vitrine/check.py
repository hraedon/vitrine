"""The provenance gate — referential invariants over a loaded corpus.

See docs/fact-model.md "Invariants". Structural validation (types, enum
values) already happened in the loader; this checks that every fact is
verifiable: sources resolve, assumptions resolve, ids are unique and honest,
and nothing verifiability-critical is blank.
"""

from __future__ import annotations

import math
import re
from html.parser import HTMLParser
from pathlib import Path

from vitrine import money
from vitrine.model import (
    INTERPOLATION_RE,
    Basis,
    BlockKind,
    Corpus,
    DerivedOp,
    Fact,
    Room,
    measure_axis,
    normalized_unit,
)
from vitrine.series import Series


def _quantity_renderings(quantity: float) -> set[str]:
    """The strings a structured quantity may appear as in the display value.

    The quantity is a transcription of the displayed datum; if none of these
    renderings occurs verbatim in ``value``, the two have drifted apart.
    """
    renderings = {f"{quantity:g}"}
    if quantity == int(quantity):
        renderings.add(str(int(quantity)))
        renderings.add(f"{int(quantity):,}")
    return renderings


def check_corpus(corpus: Corpus, series: dict[str, Series] | None = None) -> list[str]:
    """Return all problems found; an empty list means the gate is green."""
    problems: list[str] = []

    for source in corpus.sources.values():
        if not source.url.strip():
            problems.append(f"source {source.id!r}: empty url — facts must be verifiable")
        if not source.population.strip():
            problems.append(f"source {source.id!r}: empty population — say who was measured")

    seen: dict[str, str] = {}
    for room in corpus.rooms:
        prefix = f"{room.country}-{room.decade}-"
        room_slug = room.slug
        by_id: dict[str, Fact] = {f.id: f for f in room.facts}
        currencies: set[str] = set()
        has_priced = False

        for fact in room.facts:
            where = f"room {room_slug}, fact {fact.id!r}"

            if fact.id in seen:
                problems.append(f"{where}: duplicate fact id (also in room {seen[fact.id]})")
            seen[fact.id] = room_slug

            if not fact.id.startswith(prefix):
                problems.append(f"{where}: id must start with {prefix!r}")

            if fact.source not in corpus.sources:
                problems.append(f"{where}: unknown source {fact.source!r}")

            for assumption_id in fact.assumptions:
                if assumption_id not in corpus.assumptions:
                    problems.append(f"{where}: unknown assumption {assumption_id!r}")

            for field_name, value in (
                ("label", fact.label),
                ("value", fact.value),
                ("unit", fact.unit),
            ):
                if not value.strip():
                    problems.append(f"{where}: empty {field_name}")

            if fact.amount_minor is not None:
                has_priced = True
                if not fact.currency.strip():
                    problems.append(f"{where}: amount_minor set but currency is empty")
                elif not money.is_known(fact.currency):
                    problems.append(
                        f"{where}: unknown currency {fact.currency!r} — register it "
                        f"in vitrine.money.CURRENCIES"
                    )
                if fact.price_year is None:
                    problems.append(f"{where}: amount_minor set but price_year is missing")
                if fact.basis is None:
                    problems.append(f"{where}: amount_minor set but basis is missing")
                elif fact.currency.strip():
                    currencies.add(fact.currency)
            elif fact.basis is not None:
                problems.append(f"{where}: basis set but amount_minor is missing")

            if fact.quantity is not None:
                if not math.isfinite(fact.quantity):
                    problems.append(f"{where}: quantity is not a finite number")
                elif not any(r in fact.value for r in _quantity_renderings(fact.quantity)):
                    problems.append(
                        f"{where}: quantity {fact.quantity:g} does not appear in the "
                        f"display value — the structured quantity must transcribe "
                        f"the displayed datum, never introduce a new number"
                    )

        if has_priced:
            has_total = any(f.basis is Basis.TOTAL for f in room.facts)
            if has_total and not room.wage_anchor and not room.income_anchor:
                problems.append(
                    f"room {room_slug}: has a priced fact (basis total) but no "
                    f"wage_anchor or income_anchor declared"
                )

            if len(currencies) > 1:
                problems.append(
                    f"room {room_slug}: inconsistent currencies {sorted(currencies)} "
                    f"among structured facts"
                )

        problems.extend(_check_derived(corpus, room, by_id, seen, series))

        for anchor_field, expected_basis, label in (
            ("wage_anchor", Basis.HOURLY, "wage_anchor"),
            ("income_anchor", Basis.ANNUAL, "income_anchor"),
        ):
            anchor_id = getattr(room, anchor_field)
            if not anchor_id:
                continue
            if anchor_id not in by_id:
                problems.append(
                    f"room {room_slug}: {label} {anchor_id!r} does not resolve "
                    f"to a fact in this room"
                )
                continue
            anchor_fact = by_id[anchor_id]
            if anchor_fact.basis is not expected_basis:
                actual = (
                    anchor_fact.basis.value
                    if anchor_fact.basis is not None
                    else "none"
                )
                problems.append(
                    f"room {room_slug}: {label} {anchor_id!r} has basis "
                    f"{actual!r}, expected {expected_basis.value!r}"
                )
            if anchor_fact.amount_minor is None:
                problems.append(
                    f"room {room_slug}: {label} {anchor_id!r} has no amount_minor"
                )
            elif anchor_fact.amount_minor == 0:
                problems.append(
                    f"room {room_slug}: {label} {anchor_id!r} has amount_minor = 0 "
                    f"(would cause division by zero)"
                )

            # An anchor's source must declare what it *measures*: you cannot
            # divide by a denominator without saying whether it is money income,
            # wages-only, a survey reconstruction, etc. The cross-decade
            # comparator relies on this to refuse incomparable series.
            anchor_source = corpus.sources.get(anchor_fact.source)
            if anchor_source is not None:
                if anchor_source.measure is None:
                    problems.append(
                        f"room {room_slug}: {label} {anchor_id!r} source "
                        f"{anchor_fact.source!r} declares no measure — an anchor "
                        f"denominator must say what it measures"
                    )
                elif measure_axis(anchor_source.measure) is not expected_basis:
                    problems.append(
                        f"room {room_slug}: {label} {anchor_id!r} source measures "
                        f"{anchor_source.measure.value!r}, which belongs to the "
                        f"{measure_axis(anchor_source.measure).value!r} axis, not "
                        f"{expected_basis.value!r}"
                    )

    return problems


def _check_derived(
    corpus: Corpus,
    room: Room,
    by_id: dict[str, Fact],
    seen: dict[str, str],
    series: dict[str, Series] | None = None,
) -> list[str]:
    """Derived facts author structure, never numbers — check the structure.

    Operands must resolve to structured facts in the same room (or, for
    cross-room derived facts, anywhere in the corpus), share a currency
    (for monetary ops), and never divide by zero; ids share the fact
    namespace and prefix rules. The value and tier are computed (plan 006),
    so there is nothing else a curator could get numerically wrong here.
    """
    problems: list[str] = []
    prefix = f"{room.country}-{room.decade}-"
    all_facts: dict[str, Fact] = {f.id: f for r in corpus.rooms for f in r.facts}
    for derived in room.derived:
        where = f"room {room.slug}, derived {derived.id!r}"

        if derived.id in seen:
            problems.append(f"{where}: duplicate id (also in room {seen[derived.id]})")
        seen[derived.id] = room.slug

        if not derived.id.startswith(prefix):
            problems.append(f"{where}: id must start with {prefix!r}")

        for field_name, value in (("label", derived.label), ("unit", derived.unit)):
            if not value.strip():
                problems.append(f"{where}: empty {field_name}")

        for assumption_id in derived.assumptions:
            if assumption_id not in corpus.assumptions:
                problems.append(f"{where}: unknown assumption {assumption_id!r}")

        # INFLATE (Plan 012): numerator only; the series provides the ratio.
        if derived.op is DerivedOp.INFLATE:
            operand = by_id.get(derived.numerator) or all_facts.get(derived.numerator)
            if operand is None:
                problems.append(
                    f"{where}: numerator {derived.numerator!r} does not resolve "
                    f"to a fact in this room or the corpus"
                )
            elif operand.amount_minor is None:
                problems.append(
                    f"{where}: numerator {derived.numerator!r} has no amount_minor"
                )
            if not derived.inflate_series:
                problems.append(f"{where}: INFLATE op requires inflate_series")
            elif series is not None and derived.inflate_series not in series:
                problems.append(
                    f"{where}: inflate_series {derived.inflate_series!r} not found"
                )
            else:
                s = series[derived.inflate_series] if series else None
                if s is not None:
                    if s.values_minor:
                        # Plan 023 WI-3: INFLATE multiplies by a series *ratio*;
                        # a monetary series is an amount, not an index — using
                        # one as the ratio smuggles a currency into the result.
                        problems.append(
                            f"{where}: inflate_series {derived.inflate_series!r} "
                            f"is monetary (values_minor) — INFLATE requires an "
                            f"index series (values)"
                        )
                    for yr, label in (
                        (derived.inflate_from_year, "inflate_from_year"),
                        (derived.inflate_to_year, "inflate_to_year"),
                    ):
                        if not yr:
                            problems.append(f"{where}: {label} is missing")
                        elif yr not in s.values and yr not in s.values_minor:
                            problems.append(
                                f"{where}: {label} {yr} not in series "
                                f"{derived.inflate_series!r}"
                            )
            continue

        # COUNT_ABOVE (Plan 027 WI-6): operands are series, not facts. The
        # candidate set must resolve entirely, be float-valued (a monetary
        # series is an amount, not a quantity to threshold), share one unit
        # (the WI-022 lesson generalized: thresholding pounds against index
        # points is dimensionally meaningless), and at least one series must
        # publish the count year. Unused fact-operand fields are refused so a
        # cargo-culted numerator cannot sit silently beside the real inputs.
        if derived.op is DerivedOp.COUNT_ABOVE:
            if not derived.count_series:
                problems.append(f"{where}: COUNT_ABOVE requires a non-empty count_series")
                continue
            if len(set(derived.count_series)) != len(derived.count_series):
                problems.append(
                    f"{where}: count_series lists a series twice — each entry counts"
                )
                continue
            if derived.numerator or derived.denominator:
                problems.append(
                    f"{where}: COUNT_ABOVE takes series operands, not fact "
                    f"operands — numerator/denominator must be omitted"
                )
            if not derived.threshold > 0:
                problems.append(f"{where}: COUNT_ABOVE requires threshold > 0")
            if not derived.at_year:
                problems.append(f"{where}: COUNT_ABOVE requires at_year")
            if series is None:
                continue
            resolved = [series[sid] for sid in derived.count_series if sid in series]
            for sid in derived.count_series:
                if sid not in series:
                    problems.append(
                        f"{where}: count_series {sid!r} not found in the series registry"
                    )
            units = {normalized_unit(s.unit) for s in resolved}
            if len(units) > 1:
                problems.append(
                    f"{where}: count_series units differ ({sorted(units)}) — "
                    f"a count is only meaningful over one dimension"
                )
            for s in resolved:
                if s.values_minor:
                    problems.append(
                        f"{where}: count_series {s.id!r} is monetary "
                        f"(values_minor) — COUNT_ABOVE thresholds quantities"
                    )
            if resolved and not any(derived.at_year in s.values for s in resolved):
                problems.append(
                    f"{where}: no listed series has a value at at_year "
                    f"{derived.at_year} — the count would be over an empty record"
                )
            continue

        # PRODUCT (WI-5): numerator.amount_minor * denominator.quantity
        if derived.op is DerivedOp.PRODUCT:
            num = by_id.get(derived.numerator) or all_facts.get(derived.numerator)
            den = by_id.get(derived.denominator) or all_facts.get(derived.denominator)
            if num is None:
                problems.append(
                    f"{where}: numerator {derived.numerator!r} does not resolve "
                    f"to a fact in this room or the corpus"
                )
            elif num.amount_minor is None:
                problems.append(
                    f"{where}: numerator {derived.numerator!r} has no amount_minor"
                )
            if den is None:
                problems.append(
                    f"{where}: denominator {derived.denominator!r} does not resolve "
                    f"to a fact in this room or the corpus"
                )
            elif den.quantity is None:
                problems.append(
                    f"{where}: denominator {derived.denominator!r} has no quantity"
                )
            continue

        # QUANTITY_RATIO (WI-5): numerator.quantity / denominator.quantity.
        # The two operands must carry comparable units (WI-022): a ratio of
        # hours to a CPI index is dimensionally meaningless and the gate must
        # refuse it rather than produce a plausible-looking number. Units are
        # authored display strings, so exact equality is the conservative test;
        # a curator ratioing two equivalent-but-differently-described quantities
        # normalizes the unit string (the corpus already does this for CPI).
        if derived.op is DerivedOp.QUANTITY_RATIO:
            num = by_id.get(derived.numerator) or all_facts.get(derived.numerator)
            den = by_id.get(derived.denominator) or all_facts.get(derived.denominator)
            if num is None:
                problems.append(
                    f"{where}: numerator {derived.numerator!r} does not resolve "
                    f"to a fact in this room or the corpus"
                )
            elif num.quantity is None:
                problems.append(
                    f"{where}: numerator {derived.numerator!r} has no quantity"
                )
            if den is None:
                problems.append(
                    f"{where}: denominator {derived.denominator!r} does not resolve "
                    f"to a fact in this room or the corpus"
                )
            elif den.quantity is None:
                problems.append(
                    f"{where}: denominator {derived.denominator!r} has no quantity"
                )
            elif den.quantity == 0:
                problems.append(
                    f"{where}: denominator {derived.denominator!r} quantity is zero"
                )
            if (
                num is not None
                and num.quantity is not None
                and den is not None
                and den.quantity is not None
                and normalized_unit(num.unit) != normalized_unit(den.unit)
            ):
                problems.append(
                    f"{where}: unit mismatch ({num.unit!r} vs {den.unit!r}) — "
                    f"a quantity_ratio divides like quantities; if these share "
                    f"a dimension, harmonize the unit strings (the distinction "
                    f"belongs in label/notes), otherwise the ratio is not "
                    f"meaningful"
                )
            continue

        # RATIO and PCT_OF: both operands must be structured monetary facts
        operands: list[Fact] = []
        for role, operand_id in (
            ("numerator", derived.numerator),
            ("denominator", derived.denominator),
        ):
            operand = by_id.get(operand_id) or all_facts.get(operand_id)
            if operand is None:
                problems.append(
                    f"{where}: {role} {operand_id!r} does not resolve to a fact "
                    f"in this room or the corpus"
                )
                continue
            if operand.amount_minor is None:
                problems.append(
                    f"{where}: {role} {operand_id!r} has no amount_minor — "
                    f"derivations divide structured amounts only"
                )
                continue
            operands.append(operand)

        if len(operands) == 2:
            numerator, denominator = operands
            if denominator.amount_minor == 0:
                problems.append(
                    f"{where}: denominator {denominator.id!r} has amount_minor = 0"
                )
            if numerator.currency != denominator.currency:
                problems.append(
                    f"{where}: currency mismatch ({numerator.currency!r} vs "
                    f"{denominator.currency!r})"
                )
    return problems


def check_render_coverage(corpus: Corpus, build_dir: Path) -> list[str]:
    """Invariant 7: the set of facts rendered must equal the set curated.

    Compares ``facts-manifest.txt`` in *build_dir* against the loaded corpus.
    An empty list means every curated fact was rendered and nothing extra
    was injected.
    """
    manifest_path = build_dir / "facts-manifest.txt"
    if not manifest_path.is_file():
        return [
            f"render-coverage: {manifest_path} not found — run 'vitrine build' first"
        ]

    rendered_ids = {
        line.strip()
        for line in manifest_path.read_text().splitlines()
        if line.strip()
    }
    curated_ids = {fact.id for room in corpus.rooms for fact in room.facts}
    curated_ids |= {derived.id for room in corpus.rooms for derived in room.derived}

    problems: list[str] = []
    for fid in sorted(curated_ids - rendered_ids):
        problems.append(f"render-coverage: fact {fid!r} curated but not rendered")
    for fid in sorted(rendered_ids - curated_ids):
        problems.append(f"render-coverage: fact {fid!r} rendered but not curated")
    return problems


def check_series(series: dict[str, Series], corpus: Corpus) -> list[str]:
    """Plan 010 series gate invariants.

    The loader already enforced types (integer years, numeric values, valid
    tier/measure). This checks referential integrity and the cross-entity rules
    that need both layers: source resolution, the exactly-one-values rule, id
    collision with facts (shared namespace), affordability-axis measure
    requirements, and the series/fact drift detector.
    """
    problems: list[str] = []

    fact_ids = {fact.id for room in corpus.rooms for fact in room.facts}
    fact_ids |= {derived.id for room in corpus.rooms for derived in room.derived}

    # Group facts by source for the drift detector (invariant 9). Only
    # structured facts (amount_minor or quantity) can drift against a series.
    facts_by_source: dict[str, list[Fact]] = {}
    for room in corpus.rooms:
        for fact in room.facts:
            if fact.amount_minor is not None or fact.quantity is not None:
                facts_by_source.setdefault(fact.source, []).append(fact)

    for s in series.values():
        where = f"series {s.id!r}"

        if not s.values and not s.values_minor:
            problems.append(f"{where}: has neither 'values' nor 'values_minor'")
        if s.values and s.values_minor:
            problems.append(
                f"{where}: has both 'values' and 'values_minor' — declare exactly one"
            )

        if s.source not in corpus.sources:
            problems.append(f"{where}: unknown source {s.source!r}")

        if s.id in fact_ids:
            problems.append(
                f"{where}: id collides with a fact id (shared namespace)"
            )

        # An affordability-axis series (income/wage denominator) inherits the
        # same measure requirement as a room anchor: you cannot divide by a
        # series without saying what it measures.
        if s.measure is not None and s.source in corpus.sources:
            src = corpus.sources[s.source]
            if src.measure is None:
                problems.append(
                    f"{where}: declares measure {s.measure.value!r} but its "
                    f"source {s.source!r} declares no measure"
                )

        if s.splices_from and s.splices_from not in series:
            problems.append(
                f"{where}: splices_from {s.splices_from!r} resolves to no series"
            )
        elif (
            s.splices_from
            and s.splices_from in series
            and s.currency != series[s.splices_from].currency
        ):
            # Plan 023 WI-3: a splice chains two series into one; chaining
            # across currencies would launder an exchange-rate conversion into
            # the corpus through the back door. The museum never converts.
            problems.append(
                f"{where}: splices_from {s.splices_from!r} carries currency "
                f"{series[s.splices_from].currency!r} but this series declares "
                f"{s.currency!r} — a splice must stay within one currency"
            )

        # Plan 023 WI-3: a monetary series must name a currency the money
        # registry knows (same rule as a priced fact), so every consumer
        # scales it by the registry's minor digits instead of assuming cents.
        if s.values_minor and s.currency and not money.is_known(s.currency):
            problems.append(
                f"{where}: unknown currency {s.currency!r} — register it in "
                f"vitrine.money.CURRENCIES"
            )

        # ── Drift detector (invariant 9) ───────────────────────────────────
        # Where a single series is the unique series for its source, a decade
        # fact from that source whose price_year the series covers must agree.
        # When two series share a source (e.g. all-family vs 4-person F-8
        # medians, which legitimately differ) the 1:1 correspondence is
        # ambiguous, so we skip rather than false-positive.
        same_source = [other for other in series.values() if other.source == s.source]
        if len(same_source) != 1:
            continue
        for fact in facts_by_source.get(s.source, []):
            year = fact.price_year
            if year is None:
                continue
            if (
                fact.amount_minor is not None
                and year in s.values_minor
                and fact.amount_minor != s.values_minor[year]
            ):
                problems.append(
                    f"{where}: disagrees with fact {fact.id!r} for {year} "
                    f"(series {s.values_minor[year]}, fact {fact.amount_minor}) "
                    f"— the same number drifted in two places"
                )
            if (
                fact.quantity is not None
                and year in s.values
                and not math.isclose(
                    fact.quantity, s.values[year], rel_tol=1e-3, abs_tol=0.05
                )
            ):
                # The fact displays the series value rounded to its display
                # precision (CPI to 1 decimal), so abs_tol covers 1-dp rounding
                # while rel_tol still catches a real drift at large magnitudes.
                problems.append(
                    f"{where}: disagrees with fact {fact.id!r} for {year} "
                    f"(series {s.values[year]:g}, fact quantity "
                    f"{fact.quantity:g}) — the same number drifted in two places"
                )
            # Cross-unit agreement: a wage series carries its annual mean in
            # ``values`` (float dollars, sub-cent precision that ``values_minor``
            # can't represent), while the matching fact stores the rounded
            # display value in ``amount_minor`` (cents). Compare dollars to
            # cents-to-dollars with cent-rounding tolerance so a drifted wage
            # is caught even though the two live in different unit fields. The
            # basis guard skips a weekly-earnings fact that shares the hourly
            # series's source but is a different concept (hourly ≠ weekly).
            if (
                fact.amount_minor is not None
                and fact.basis is Basis.HOURLY
                and year in s.values
                and not math.isclose(
                    s.values[year], fact.amount_minor / 100.0, rel_tol=1e-3, abs_tol=0.01
                )
            ):
                problems.append(
                    f"{where}: disagrees with fact {fact.id!r} for {year} "
                    f"(series {s.values[year]:g}, fact ${fact.amount_minor / 100:.2f}) "
                    f"— the same number drifted in two places"
                )

    return problems


# ── the docent numeral gate (plan 016) ────────────────────────────────────────
# Essay prose is editorial voice, but its numbers must all be bound to facts
# by interpolation. Stripping the ``{fact:...}`` bindings, the only numerals
# allowed bare are four-digit years (1850–2035), decade words, and ranges of
# the two. Everything else — percentages, dollars, hours, counts — fails.

_YEAR = r"(?:18[5-9]\d|19\d\d|20(?:[01]\d|2\d|3[0-5]))"
_TOKEN_OK = re.compile(rf"(?:{_YEAR}s?(?:[-–—]{_YEAR}s?)?)")
_EDGE_PUNCT = ".,;:!?()[]{}\"'“”‘’*·—–-"  # noqa: RUF001 — punctuation strip set, not prose
_SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]*")


def _unbound_numerals(text: str) -> list[str]:
    """Prose tokens carrying a digit that isn't an allowed year/decade."""
    stripped = INTERPOLATION_RE.sub(" ", text)
    bad: list[str] = []
    for token in stripped.split():
        core = token.strip(_EDGE_PUNCT)
        if not any(character.isdigit() for character in core):
            continue
        if not _TOKEN_OK.fullmatch(core):
            bad.append(token)
    return bad


def check_essays(corpus: Corpus) -> list[str]:
    """The docent gate: prose may interpret, but every numeral is bound.

    Chart-block *slugs* (arc/group/metric) are validated at build time in the
    presentation layer, which owns those registries — the core gate validates
    block shape, ids, interpolation resolution, and the numeral rule.
    """
    problems: list[str] = []
    curated_ids = {fact.id for room in corpus.rooms for fact in room.facts}
    curated_ids |= {derived.id for room in corpus.rooms for derived in room.derived}

    seen_slugs: set[str] = set()
    for essay in corpus.essays:
        where = f"essay {essay.slug!r}"
        if not _SLUG_RE.fullmatch(essay.slug):
            problems.append(f"{where}: slug must be lowercase alphanumerics and hyphens")
        if essay.slug in seen_slugs:
            problems.append(f"{where}: duplicate essay slug")
        seen_slugs.add(essay.slug)
        if not essay.title.strip():
            problems.append(f"{where}: empty title")
        if not essay.standfirst.strip():
            problems.append(f"{where}: empty standfirst")
        if not essay.blocks:
            problems.append(f"{where}: an essay needs at least one block")
            continue

        bound = False
        for token in _unbound_numerals(essay.title) + _unbound_numerals(essay.standfirst):
            problems.append(
                f"{where}: unbound numeral {token!r} in head matter — bind it "
                f"with {{fact:<id>}} or write it in words"
            )
        if INTERPOLATION_RE.search(essay.standfirst):
            bound = True
        for match in INTERPOLATION_RE.finditer(essay.standfirst):
            if match.group(1) not in curated_ids:
                problems.append(
                    f"{where}: standfirst cites unknown fact {match.group(1)!r}"
                )

        for i, block in enumerate(essay.blocks, start=1):
            block_where = f"{where}, block {i}"
            if block.kind is BlockKind.PROSE:
                if not block.text.strip():
                    problems.append(f"{block_where}: prose block with empty text")
                    continue
                for token in _unbound_numerals(block.text):
                    problems.append(
                        f"{block_where}: unbound numeral {token!r} — bind it "
                        f"with {{fact:<id>}} or write it in words"
                    )
                for match in INTERPOLATION_RE.finditer(block.text):
                    bound = True
                    if match.group(1) not in curated_ids:
                        problems.append(
                            f"{block_where}: cites unknown fact {match.group(1)!r}"
                        )
            else:
                slugs = [s for s in (block.arc, block.group, block.metric) if s]
                if len(slugs) != 1:
                    problems.append(
                        f"{block_where}: chart block must name exactly one of "
                        f"arc/group/metric"
                    )
                else:
                    bound = True
                if block.text.strip():
                    problems.append(f"{block_where}: chart blocks carry no prose text")
        if not bound:
            problems.append(
                f"{where}: an essay must engage the record — at least one fact "
                f"interpolation or chart block"
            )
    return problems


class _MarkScanner(HTMLParser):
    """Collects every ``data-fact-id`` attribute in a built page."""

    def __init__(self) -> None:
        super().__init__()
        self.mark_ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "data-fact-id" and value:
                self.mark_ids.append(value)


def check_mark_coverage(corpus: Corpus, build_dir: Path) -> list[str]:
    """Plan 007 D2: every rendered mark must resolve to a curated fact.

    Scans every built page for ``data-fact-id`` (chart points, stage glyphs,
    meter segments, cutaway annotations). A mark that can't name its fact
    doesn't render — this catches one that named a fact the corpus doesn't
    have. Verified from the built HTML, not the renderer's word for it.
    """
    pages = sorted(build_dir.rglob("*.html"))
    if not pages:
        return [f"mark-coverage: no built pages under {build_dir} — run 'vitrine build' first"]

    curated_ids = {fact.id for room in corpus.rooms for fact in room.facts}
    curated_ids |= {derived.id for room in corpus.rooms for derived in room.derived}

    problems: list[str] = []
    n_marks = 0
    for page in pages:
        scanner = _MarkScanner()
        scanner.feed(page.read_text())
        n_marks += len(scanner.mark_ids)
        for mark_id in sorted(set(scanner.mark_ids) - curated_ids):
            problems.append(
                f"mark-coverage: {page.relative_to(build_dir)} carries mark "
                f"{mark_id!r} that resolves to no curated fact"
            )
    if n_marks == 0:
        problems.append(
            "mark-coverage: no data-fact-id marks found in any built page — "
            "the chart surfaces are missing"
        )
    return problems
