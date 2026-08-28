"""Command-line entry point for the gate, build, export, and gap inventory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vitrine.check import (
    check_corpus,
    check_essays,
    check_mark_coverage,
    check_render_coverage,
    check_series,
)
from vitrine.export import export_corpus
from vitrine.gaps import format_report, room_gaps
from vitrine.loader import LoadError, load_corpus
from vitrine.publish import OutputError, copy_existing_tree, staged_directory
from vitrine.series import SeriesError, load_series


def _cmd_check(data_dir: Path, build_dir: Path | None = None) -> int:
    try:
        corpus = load_corpus(data_dir)
    except LoadError as exc:
        print(f"LOAD ERROR: {exc}", file=sys.stderr)
        return 1
    try:
        series = load_series(data_dir)
    except SeriesError as exc:
        print(f"LOAD ERROR: {exc}", file=sys.stderr)
        return 1
    problems = check_corpus(corpus, series)
    problems.extend(check_series(series, corpus))
    problems.extend(check_essays(corpus))
    if build_dir is not None:
        problems.extend(check_render_coverage(corpus, build_dir))
        problems.extend(check_mark_coverage(corpus, build_dir))
    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if problems:
        print(f"{len(problems)} problem(s).", file=sys.stderr)
        return 1
    n_facts = sum(len(room.facts) for room in corpus.rooms)
    n_derived = sum(len(room.derived) for room in corpus.rooms)
    print(
        f"ok: {len(corpus.rooms)} room(s), {n_facts} fact(s), {n_derived} derived, "
        f"{len(corpus.sources)} source(s), {len(corpus.assumptions)} assumption(s), "
        f"{len(series)} series, {len(corpus.essays)} essay(s)"
    )
    if build_dir is not None:
        print(f"render-coverage: verified ({n_facts + n_derived} exhibits match build)")
        print("mark-coverage: every rendered mark resolves to a curated fact")
    return 0


def _cmd_build(data_dir: Path, out_dir: Path) -> int:
    # The gate runs first: nothing unverifiable gets rendered.
    status = _cmd_check(data_dir)
    if status != 0:
        return status
    try:
        from vitrine.site.build import build_site as render_site
    except ImportError:
        print(
            "build requires the [site] extra: uv pip install -e '.[site]'",
            file=sys.stderr,
        )
        return 1
    corpus = load_corpus(data_dir)
    series = load_series(data_dir)
    try:
        render_site(corpus, out_dir, series, data_dir)
    except (OutputError, OSError) as exc:
        print(f"OUTPUT ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"built → {out_dir}")
    return 0


def _cmd_gaps(data_dir: Path) -> int:
    try:
        corpus = load_corpus(data_dir)
    except LoadError as exc:
        print(f"LOAD ERROR: {exc}", file=sys.stderr)
        return 1
    print(format_report(room_gaps(corpus)))
    return 0


def _cmd_export(data_dir: Path, out_dir: Path) -> int:
    """Validate and write the corpus exports plus their landing page."""
    status = _cmd_check(data_dir)
    if status != 0:
        return status
    try:
        from vitrine.site.build import build_data_page
    except ImportError:
        print(
            "export requires the [site] extra: uv pip install -e '.[site]'",
            file=sys.stderr,
        )
        return 1
    try:
        corpus = load_corpus(data_dir)
        series = load_series(data_dir)
    except (LoadError, SeriesError) as exc:
        print(f"LOAD ERROR: {exc}", file=sys.stderr)
        return 1
    try:
        with staged_directory(
            out_dir,
            forbidden_paths=(data_dir,),
            cleanup_roots=(out_dir, out_dir / "data"),
        ) as staging:
            copy_existing_tree(out_dir, staging)
            export_corpus(
                corpus,
                staging,
                series,
                source_dir=data_dir,
                lock_root=out_dir,
            )
            build_data_page(corpus, staging)
    except (OutputError, OSError) as exc:
        print(f"OUTPUT ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"exported → {out_dir}")
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
    export = sub.add_parser("export", help="export the corpus as JSON and CSV")
    export.add_argument(
        "--out", type=Path, default=Path("_site"), help="output directory (default: ./_site)"
    )
    sub.add_parser("gaps", help="print the mechanical gap inventory (generated, never hand-kept)")

    args = parser.parse_args(argv)
    if args.command == "check":
        return _cmd_check(args.data, args.against_build)
    if args.command == "build":
        return _cmd_build(args.data, args.out)
    if args.command == "export":
        return _cmd_export(args.data, args.out)
    if args.command == "gaps":
        return _cmd_gaps(args.data)
    raise AssertionError(f"unhandled command {args.command!r}")


if __name__ == "__main__":
    sys.exit(main())
