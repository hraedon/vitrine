"""Command-line entry point: `vitrine check` (the gate) and `vitrine build`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vitrine.check import check_corpus, check_render_coverage
from vitrine.loader import LoadError, load_corpus


def _cmd_check(data_dir: Path, build_dir: Path | None = None) -> int:
    try:
        corpus = load_corpus(data_dir)
    except LoadError as exc:
        print(f"LOAD ERROR: {exc}", file=sys.stderr)
        return 1
    problems = check_corpus(corpus)
    if build_dir is not None:
        problems.extend(check_render_coverage(corpus, build_dir))
    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if problems:
        print(f"{len(problems)} problem(s).", file=sys.stderr)
        return 1
    n_facts = sum(len(room.facts) for room in corpus.rooms)
    print(
        f"ok: {len(corpus.rooms)} room(s), {n_facts} fact(s), "
        f"{len(corpus.sources)} source(s), {len(corpus.assumptions)} assumption(s)"
    )
    if build_dir is not None:
        print(f"render-coverage: verified ({n_facts} facts match build)")
    return 0


def _cmd_build(data_dir: Path, out_dir: Path) -> int:
    # The gate runs first: nothing unverifiable gets rendered.
    status = _cmd_check(data_dir)
    if status != 0:
        return status
    try:
        from vitrine.site.render import render_site
    except ImportError:
        print(
            "build requires the [site] extra: uv pip install -e '.[site]'",
            file=sys.stderr,
        )
        return 1
    corpus = load_corpus(data_dir)
    render_site(corpus, out_dir)
    print(f"built → {out_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vitrine")
    parser.add_argument(
        "--data", type=Path, default=Path("data"), help="data directory (default: ./data)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="validate the data against the fact model")
    check_parser.add_argument(
        "--against-build",
        type=Path,
        default=None,
        help="also verify rendered facts in this build dir match the curated corpus",
    )
    build = sub.add_parser("build", help="render the static site")
    build.add_argument(
        "--out", type=Path, default=Path("_site"), help="output directory (default: ./_site)"
    )

    args = parser.parse_args(argv)
    if args.command == "check":
        return _cmd_check(args.data, args.against_build)
    if args.command == "build":
        return _cmd_build(args.data, args.out)
    raise AssertionError(f"unhandled command {args.command!r}")


if __name__ == "__main__":
    sys.exit(main())
