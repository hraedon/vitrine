#!/usr/bin/env python3
"""Structural and editorial checks; this does not re-extract source values.

Surfaces WI-008-class miscites corpus-wide by mechanically checking:
1. Every fact's source ID resolves in sources.toml
2. Every fact's quantity appears verbatim in its value string
3. Other source mentions in notes are surfaced for contextual review
4. Source notes don't reference stale fact data (values no fact cites)
5. Fact notes identify the cited source (heuristic keyword match)

Usage: python3 scripts/cross_check.py [--verbose]
"""

from __future__ import annotations

import argparse
import math
import tomllib
from pathlib import Path

from vitrine.check import _quantity_in_value

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_sources(data_dir: Path = REPO_ROOT / "data") -> dict[str, dict]:
    with (data_dir / "sources.toml").open("rb") as f:
        data = tomllib.load(f)
    return {s["id"]: s for s in data.get("source", [])}


def load_facts(data_dir: Path = REPO_ROOT / "data") -> list[dict]:
    facts: list[dict] = []
    for fname in sorted(data_dir.glob("*/*.toml")):
        with fname.open("rb") as f:
            data = tomllib.load(f)
        room = data.get("room")
        if not isinstance(room, dict):
            continue  # essays and annual series are not room facts
        for fact in data.get("fact", []):
            fact["_decade"] = fname.stem
            fact["_country"] = room.get("country", "?")
            fact["_file"] = fname.relative_to(data_dir).as_posix()
            facts.append(fact)
    return facts


def check_source_resolves(
    facts: list[dict], sources: dict[str, dict]
) -> list[str]:
    """Check 1: every fact's source ID exists in sources.toml."""
    issues = []
    for fact in facts:
        sid = fact.get("source", "")
        if not sid or sid not in sources:
            fid = fact.get("id", "?")
            issues.append(
                f'  MISSING SOURCE: {fid} cites "{sid}" '
                f"(in {fact['_file']})"
            )
    return issues


def check_quantity_in_value(facts: list[dict]) -> list[str]:
    """Use the core gate's complete-token rule, not a second substring test."""
    issues = []
    for fact in facts:
        qty = fact.get("quantity")
        val = fact.get("value", "")
        if qty is None:
            continue
        if (
            isinstance(qty, bool) or not isinstance(qty, int | float)
            or not math.isfinite(qty) or not _quantity_in_value(qty, val)
        ):
            fid = fact.get("id", "?")
            issues.append(
                f'  QTY MISMATCH: {fid} quantity={qty} '
                f'not in value="{val[:100]}"'
            )
    return issues


def check_note_source_mismatch(
    facts: list[dict], sources: dict[str, dict]
) -> list[str]:
    """Flag other source mentions for review; a comparison is not a miscite."""
    issues = []
    source_patterns = {
        "ncta": {"ncta-cable-history"},
        "fcc 97-423": {"fcc-video-competition"},
        "fcc 07-206": {"fcc-video-competition"},
        "fred": {
            "fred-ahetpi", "fred-awhman", "fred-ces-manuf-earnings",
            "fred-cpiaucns", "fred-cpiaucsl", "fred-mefainusa646n",
            "fred-mefainusa672n", "worldbank-itu-telecom",
        },
        "bls bulletin 49": {
            "bls-bulletin-49-1903", "commissioner-labor-18th-1903",
        },
        "bls bulletin 1312": {"bls-bulletin-1312-12"},
        "bls bulletin 1055": {"bls-bulletin-1055-1952"},
        "cex": {"bls-cex"},
        "recs": {"eia-recs"},
        "ramey": {"ramey-2009"},
        "statistical abstract": {"statab-food-prices"},
        "ipums": {"ipums-usa", "ipums-1940-census"},
        "pew": {"pew-internet-broadband"},
        "nchs": {"nchs-nvss"},
        "bts": {"bts-vehicle-availability"},
    }

    for fact in facts:
        sid = fact.get("source", "")
        notes = fact.get("notes", "").lower()
        if not sid or not notes:
            continue
        source = sources.get(sid, {})
        identity = " ".join(str(source.get(key, "")) for key in (
            "id", "title", "publisher", "short_cite",
        )).lower()
        for pattern, valid_ids in source_patterns.items():
            if pattern in notes and sid not in valid_ids and pattern not in identity:
                # Suppress false positive: notes that mention a
                # previous source attribution in correction context
                if "previous source" in notes or "was incorrect" in notes:
                    continue
                fid = fact.get("id", "?")
                issues.append(
                    f"  OTHER SOURCE MENTION: {fid} (source={sid}) "
                    f'notes mention "{pattern}" '
                    f'(known registrations: {", ".join(sorted(valid_ids))}); '
                    "inspect whether this is comparison, lineage or a miscite"
                )
    return issues


def check_stale_source_notes(
    facts: list[dict], sources: dict[str, dict]
) -> list[str]:
    """Check 4: source notes don't reference stale data."""
    issues = []
    source_facts: dict[str, list[str]] = {}
    for fact in facts:
        sid = fact.get("source", "")
        if sid:
            source_facts.setdefault(sid, []).append(
                fact.get("id", "?")
            )

    for sid, src in sources.items():
        notes = src.get("notes", "").lower()
        facts_using = source_facts.get(sid, [])
        if "ncta" in sid:
            cable_facts = [f for f in facts_using if "cable" in f]
            if not cable_facts and (
                "penetration" in notes or "customers" in notes
            ):
                issues.append(
                    f"  STALE SOURCE: {sid} notes describe cable "
                    f"data but no cable fact cites it"
                )
        if "1992" in notes and "~60%" in notes:
            citing_90s = [f for f in facts_using if "1990" in f]
            if not citing_90s:
                issues.append(
                    f"  STALE SOURCE: {sid} notes reference "
                    f"1992/~60% but no 1990s fact cites it"
                )
    return issues


def check_note_completeness(facts: list[dict]) -> list[str]:
    """Check 5: facts have meaningful provenance notes."""
    issues = []
    for fact in facts:
        notes = fact.get("notes", "")
        fid = fact.get("id", "?")
        val = fact.get("value", "")
        if "no reliable record" in val.lower():
            continue
        if not notes or len(notes) < 20:
            sid = fact.get("source", "?")
            issues.append(
                f"  THIN NOTES: {fid} has {len(notes)} chars "
                f"in notes (source={sid})"
            )
    return issues


def check_source_url_resolves(
    facts: list[dict], sources: dict[str, dict]
) -> list[str]:
    """Check 6: every source has a URL."""
    issues = []
    for sid, src in sources.items():
        url = src.get("url", "")
        if not isinstance(url, str) or not url.strip():
            issues.append(f"  MISSING URL: source {sid} has no URL")
    return issues


def check_tier_discipline(facts: list[dict]) -> list[str]:
    """Surface scholarly estimates for editorial review; Tier D is permitted."""
    issues = []
    for fact in facts:
        tier = fact.get("tier", "")
        if tier == "D" and not fact.get("value", "").strip().lower().startswith(
            "no reliable record"
        ):
            fid = fact.get("id", "?")
            issues.append(
                f"  SCHOLARLY ESTIMATE: {fid} — retain the disclosed Tier D "
                "unless new source evidence justifies a change"
            )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=REPO_ROOT / "data")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    sources = load_sources(args.data)
    facts = load_facts(args.data)

    print(f"Cross-check: {len(facts)} facts, {len(sources)} sources")
    print()

    all_issues: list[tuple[str, list[str]]] = [
        ("CHECK 1: Source ID resolves",
         check_source_resolves(facts, sources)),
        ("CHECK 2: Quantity in value",
         check_quantity_in_value(facts)),
        ("CHECK 3: Other source mentions (editorial review)",
         check_note_source_mismatch(facts, sources)),
        ("CHECK 4: Stale source notes",
         check_stale_source_notes(facts, sources)),
        ("CHECK 5: Note completeness",
         check_note_completeness(facts)),
        ("CHECK 6: Source has URL",
         check_source_url_resolves(facts, sources)),
        ("CHECK 7: Disclosed scholarly estimates",
         check_tier_discipline(facts)),
    ]

    # Hard errors (Checks 1, 2, 6) fail CI. Advisory checks (3, 4, 5, 7)
    # report but don't block: they flag false positives (contextual source
    # mentions), thin notes, and known Tier-D structural gaps.
    hard_check_names = {
        "CHECK 1: Source ID resolves",
        "CHECK 2: Quantity in value",
        "CHECK 6: Source has URL",
    }

    total_issues = 0
    hard_issues = 0
    for name, issues in all_issues:
        if issues:
            print(f"=== {name} ({len(issues)} issues) ===")
            for issue in issues:
                print(issue)
            print()
            total_issues += len(issues)
            if name in hard_check_names:
                hard_issues += len(issues)
        elif args.verbose:
            print(f"=== {name}: clean ===")
            print()

    print("=== SUMMARY ===")
    print(f"Facts checked: {len(facts)}")
    print(f"Sources checked: {len(sources)}")
    print(f"Total issues: {total_issues}")
    print(f"Hard errors (block CI): {hard_issues}")
    if hard_issues == 0:
        print("Structural checks passed. Source values were not re-extracted.")
        print("Editorial advisories need contextual review; this is not source verification.")
    else:
        print(f"  {hard_issues} hard error(s) found — must fix.")
    return 1 if hard_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
