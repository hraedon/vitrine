"""The provenance gate — referential invariants over a loaded corpus.

See docs/fact-model.md "Invariants". Structural validation (types, enum
values) already happened in the loader; this checks that every fact is
verifiable: sources resolve, assumptions resolve, ids are unique and honest,
and nothing verifiability-critical is blank.
"""

from __future__ import annotations

import math
from pathlib import Path

from vitrine.model import Basis, Corpus, Fact, Room, measure_axis


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


def check_corpus(corpus: Corpus) -> list[str]:
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

        problems.extend(_check_derived(corpus, room, by_id, seen))

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
) -> list[str]:
    """Derived facts author structure, never numbers — check the structure.

    Operands must resolve to structured facts in the same room, share a
    currency, and never divide by zero; ids share the fact namespace and
    prefix rules. The value and tier are computed (plan 006), so there is
    nothing else a curator could get numerically wrong here.
    """
    problems: list[str] = []
    prefix = f"{room.country}-{room.decade}-"
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

        operands: list[Fact] = []
        for role, operand_id in (
            ("numerator", derived.numerator),
            ("denominator", derived.denominator),
        ):
            operand = by_id.get(operand_id)
            if operand is None:
                problems.append(
                    f"{where}: {role} {operand_id!r} does not resolve to a fact "
                    f"in this room"
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
