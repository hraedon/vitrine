# Publication Review — Sanitization and Reuse Terms

**Status:** PASS — the working tree and the full git history contain no
work-domain identifiers, no credentials, and no redistributable third-party
microdata. The repository is safe to be public, subject to the conditions below.

**Reviewed:** 2026-07-28, covering all 152 commits and every tracked file at
`1829a34`. Checks were executed, not asserted; each is named with its command
and result in "What was checked" below.

**Re-verified:** 2026-08-14, on the `ui/statistical-atlas` line (the working
tree plus `git log -p --all` history check against the current canonical
denylist, 13 tokens) when this review and `LICENSE` were adopted from
`plan-022-multi-currency` (`8822fab`): working-tree scan exit 0, 0 matching
lines in history. Commits since the original review point are covered by the
standing identifier gate (CI job + pre-commit hook); per this document's own
rule, re-run the full review before any future change in publication posture.

**A finding about this review's timing.** This document is the gate Plan 021
Pillar IV names as a prerequisite for opening the doors — and it is being
written *after* the repository was already made public. The review passes, so
the outcome is fine, but the ordering was not: the gate ran after the event it
was supposed to gate. Two related drifts were found at the same time and are
corrected in the same change:

- Plan 021 (revised 2026-07-28) still described the project as private.
- The repository had **no LICENSE file**, which under default copyright means
  all rights reserved — the opposite of the intent for a project whose premise
  is an openly citable methodology. `LICENSE` now dual-licenses the work
  (MIT for software, CC BY-SA 4.0 for the corpus and prose).

This is the same defect class as the README drift repaired on 2026-07-28 (a
Status line claiming "zero Tier D estimates" against six): the project's
provenance discipline is rigorously turned outward at the data and had gone
unapplied to its own claims about itself. The README counts are now
machine-checked by `tests/test_docs_sync.py`. This review has no equivalent
automatic guard and is a point-in-time record; re-run it before any future
change in publication posture.

## What this is

Per `AGENTS.md` and portfolio policy: no work-domain identifiers in committed
files. The only forbidden identifiers are the work-domain set in the canonical
denylist at `~/.config/agent-suite/forbidden-identifiers`. Homelab identifiers
(`hraedon.com` and its subdomains, `mvm*` hosts, lab service accounts) are
**allowed** — `hraedon` is the published author identity, not a secret. This
review is the gate, independent of how low the risk looks.

## What was checked

| Check | Method | Result |
|---|---|---|
| Working-tree identifiers | `scripts/check_committed_identifiers.py` with `VITRINE_FORBIDDEN_IDENTIFIERS` set from the canonical 61-token denylist | **pass** (exit 0) |
| Full history, file contents | `git log -p --all` filtered against the canonical denylist (`grep -F -i -f`) | **0 matching lines** across 152 commits |
| Full history, commit metadata | commit subjects, bodies, author names and emails filtered against the denylist | **0 matching lines** |
| `samples/` never committed | `git log --all --diff-filter=A --name-only` for paths under `samples/` | **0** — the directory holding real environment data and API keys has never been tracked |
| Credentials and key material | tracked-file scan for API-key/token/password/private-key patterns | **none** — all hits are design tokens (`docs/design-spec.md`), the `secretName:` reference in `k8s/ingress.yaml`, and `AGENTS.md` documenting that API keys live in the uncommitted `samples/api.env` |
| Email addresses | tracked-file scan for address patterns | **none** |
| Raw third-party microdata | largest tracked files reviewed; search for IPUMS extract artefacts | **none** — largest files are `uv.lock`, `data/sources.toml`, and docs. `scripts/ipums_extract.py` reads local extracts that are never committed |
| Hostnames | `k8s/` manifests | `vitrine.hraedon.com` only — an allowed homelab identifier and the intended deploy target |

The identifier gate also runs in CI on every push (`.github/workflows/identifier-gate.yml`), with the `VITRINE_FORBIDDEN_IDENTIFIERS` secret configured since 2026-07-08. The gate is a no-op when the secret is absent, so a fork or fresh clone is never blocked — which also means **the gate protects this repository, not forks of it**.

## Reuse terms

`LICENSE` dual-licenses the project: **MIT** for `src/`, `tests/`, `scripts/`,
`k8s/`, `.github/` and packaging; **CC BY-SA 4.0** for `data/`, `docs/`,
`plans/`, `README.md`, `AGENTS.md`, and the rendered site. Ambiguous files take
the content license, because the corpus and methodology are the part meant to
be cited and built upon, and ShareAlike keeps derivative corpora open.

The licenses cover vitrine's own work — the code, the compilation, the tier
assignments, the source cards, the gap declarations, the prose. They do not
extend to the underlying measurements:

- **US federal statistical publications** (Census, BLS, BEA, NCHS, CMS, EIA)
  are generally not subject to copyright as works of the U.S. Government;
  their terms are the agency's.
- **IPUMS USA (Tier B facts)** — vitrine publishes only aggregate statistics
  it computed, which the IPUMS Terms of Use permit; redistribution of
  full-count microdata is prohibited and no raw extract is in this repository.
  Reuse inherits the IPUMS citation requirement. See `docs/ipums-compliance.md`.
  **Outstanding courtesy obligation:** IPUMS asks that publications using its
  data be added to the IPUMS Bibliography. That has not been done and should be,
  once the site is deployed and citable.

## Conditions

1. **`samples/` stays untracked.** It holds real environment data and API keys.
   The always-on half of `check_committed_identifiers.py` fails CI if any file
   under `samples/` is force-added; do not weaken it.
2. **The canonical denylist is the single source of truth.** Never hand-roll a
   pattern list for this repo — use `~/.config/agent-suite/forbidden-identifiers`
   verbatim, via the `publication-prep` skill.
3. **Homelab identifiers remain allowed.** Do not "sanitize" `hraedon.com`,
   `vitrine.hraedon.com`, or `mvm*` — that has been gotten backwards elsewhere in
   the portfolio, and redacting the published author identity is itself an error.
4. **Re-run this review before any change in publication posture** — a new
   deploy target, a second repository, or any import of third-party data whose
   terms are not already recorded here.
5. **New data sources carry their terms.** A source added to `data/sources.toml`
   from a non-governmental or non-US publisher needs its reuse terms understood
   before its values are rendered, not after.

## Verdict

Safe to be public. The corpus contains no secrets and no redistributable
third-party data; the history is clean across all 152 commits; reuse terms are
now explicit rather than defaulted. The process finding — that publication
preceded this review — is recorded rather than tidied away, because the point
of the gate is the ordering, and the ordering is what failed.
