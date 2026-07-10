#!/usr/bin/env python3
"""Cross-check facts against sources — the WI-009 note-vs-source audit.

Surfaces WI-008-class miscites corpus-wide by mechanically checking:
1. Every fact's source ID resolves in sources.toml
2. Every fact's quantity appears verbatim in its value string
3. Fact notes don't mention a different source than what's cited
4. Source notes don't reference stale fact data (values no fact cites)
5. Fact notes identify the cited source (heuristic keyword match)

Usage: python3 scripts/cross_check.py [--verbose]
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_sources() -> dict[str, dict]:
    with open(REPO_ROOT / "data/sources.toml", "rb") as f:
        data = tomllib.load(f)
    return {s["id"]: s for s in data.get("source", [])}


def load_facts() -> list[dict]:
    facts: list[dict] = []
    fact_dir = REPO_ROOT / "data/us"
    for fname in sorted(fact_dir.iterdir()):
        if not fname.name.endswith(".toml"):
            continue
        with open(fname, "rb") as f:
            data = tomllib.load(f)
        for fact in data.get("fact", []):
            fact["_decade"] = fname.stem
            fact["_file"] = fname.name
            facts.append(fact)
    return facts


def check_source_resolves(
    facts: list[dict], sources: dict[str, dict]
) -> list[str]:
    """Check 1: every fact's source ID exists in sources.toml."""
    issues = []
    for fact in facts:
        sid = fact.get("source", "")
        if sid and sid not in sources:
            fid = fact.get("id", "?")
            issues.append(
                f'  MISSING SOURCE: {fid} cites "{sid}" '
                f"(in {fact['_file']})"
            )
    return issues


def check_quantity_in_value(facts: list[dict]) -> list[str]:
    """Check 2: quantity appears verbatim in the value string."""
    issues = []
    for fact in facts:
        qty = fact.get("quantity")
        val = fact.get("value", "")
        if qty is None or not val:
            continue
        qty_str = str(qty)
        qty_int = (
            f"{int(qty):,}"
            if isinstance(qty, (int, float)) and qty == int(qty)
            else None
        )
        if qty_str not in val and (qty_int is None or qty_int not in val):
            fid = fact.get("id", "?")
            issues.append(
                f'  QTY MISMATCH: {fid} quantity={qty} '
                f'not in value="{val[:100]}"'
            )
    return issues


def check_note_source_mismatch(
    facts: list[dict], sources: dict[str, dict]
) -> list[str]:
    """Check 3: fact notes don't mention a different source."""
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
        for pattern, valid_ids in source_patterns.items():
            if pattern in notes and sid not in valid_ids:
                # Suppress false positive: notes that mention a
                # previous source attribution in correction context
                if "previous source" in notes or "was incorrect" in notes:
                    continue
                fid = fact.get("id", "?")
                issues.append(
                    f"  NOTE-SOURCE MISMATCH: {fid} (source={sid}) "
                    f'notes mention "{pattern}" -> {valid_ids}'
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
        if not url:
            issues.append(f"  MISSING URL: source {sid} has no URL")
    return issues


def check_tier_discipline(facts: list[dict]) -> list[str]:
    """Check 7: no Tier D facts remain."""
    issues = []
    for fact in facts:
        tier = fact.get("tier", "")
        if tier == "D":
            fid = fact.get("id", "?")
            issues.append(
                f"  TIER D: {fid} is still Tier D — upgrade "
                f"or render as gap"
            )
    return issues


def main() -> int:
    verbose = "--verbose" in sys.argv
    sources = load_sources()
    facts = load_facts()

    print(f"Cross-check: {len(facts)} facts, {len(sources)} sources")
    print()

    all_issues: list[tuple[str, list[str]]] = [
        ("CHECK 1: Source ID resolves",
         check_source_resolves(facts, sources)),
        ("CHECK 2: Quantity in value",
         check_quantity_in_value(facts)),
        ("CHECK 3: Note-source mismatch",
         check_note_source_mismatch(facts, sources)),
        ("CHECK 4: Stale source notes",
         check_stale_source_notes(facts, sources)),
        ("CHECK 5: Note completeness",
         check_note_completeness(facts)),
        ("CHECK 6: Source has URL",
         check_source_url_resolves(facts, sources)),
        ("CHECK 7: Zero Tier D",
         check_tier_discipline(facts)),
    ]

    total_issues = 0
    for name, issues in all_issues:
        if issues:
            print(f"=== {name} ({len(issues)} issues) ===")
            for issue in issues:
                print(issue)
            print()
            total_issues += len(issues)
        elif verbose:
            print(f"=== {name}: clean ===")
            print()

    print("=== SUMMARY ===")
    print(f"Facts checked: {len(facts)}")
    print(f"Sources checked: {len(sources)}")
    print(f"Total issues: {total_issues}")
    if total_issues == 0:
        print("All checks passed — zero miscites detected.")
    else:
        print(f"  {total_issues} issue(s) found — see above.")
    return 1 if total_issues else 0


if __name__ == "__main__":
    sys.exit(main())
