"""Tests for the identifier gate: parser, BOM detection, binary sniffing, scan.

These exercise the pure logic of ``scripts.check_committed_identifiers`` without
going through ``git`` — the functions are importable directly and take/return
plain data. The git-backed path collectors (``collect_tracked_paths`` etc.) are
not tested here because they shell out to git.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# ``scripts/`` is not a Python package, so import the module from its file path.
# Register in sys.modules so the module isn't garbage-collected and Violation
# instances can be pickled (they reference __module__).
_script_path = Path(__file__).parent.parent / "scripts" / "check_committed_identifiers.py"
_spec = importlib.util.spec_from_file_location("check_committed_identifiers", _script_path)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
sys.modules["check_committed_identifiers"] = _mod
_spec.loader.exec_module(_mod)

Violation = _mod.Violation
_is_binary = _mod._is_binary
_sniff_encoding = _mod._sniff_encoding
leaked_tracked_files = _mod.leaked_tracked_files
parse_identifier_set = _mod.parse_identifier_set
scan_files = _mod.scan_files
scan_text = _mod.scan_text
main = _mod.main

# ── parse_identifier_set ────────────────────────────────────────────────────


def test_parse_whitespace_separated() -> None:
    result = parse_identifier_set("alice-host bob-service")
    assert result == frozenset({"alice-host", "bob-service"})


def test_parse_one_per_line() -> None:
    result = parse_identifier_set("alice-host\nbob-service\n")
    assert result == frozenset({"alice-host", "bob-service"})


def test_parse_strips_full_line_comments() -> None:
    result = parse_identifier_set("# a comment\nalice-host\n# another\nbob-service")
    assert result == frozenset({"alice-host", "bob-service"})


def test_parse_strips_trailing_comments() -> None:
    result = parse_identifier_set("alice-host # the admin\nbob-service")
    assert result == frozenset({"alice-host", "bob-service"})


def test_parse_strips_whitespace() -> None:
    result = parse_identifier_set("  alice-host  \n\t bob-service\t")
    assert result == frozenset({"alice-host", "bob-service"})


def test_parse_deduplicates() -> None:
    result = parse_identifier_set("alice-host alice-host alice-host")
    assert result == frozenset({"alice-host"})


def test_parse_empty_returns_empty() -> None:
    assert parse_identifier_set("") == frozenset()


def test_parse_only_comments_returns_empty() -> None:
    assert parse_identifier_set("# nothing here\n# or here") == frozenset()


def test_parse_only_whitespace_returns_empty() -> None:
    assert parse_identifier_set("   \n\t\n  ") == frozenset()


def test_parse_lowercases() -> None:
    result = parse_identifier_set("Alice-Host BOB-Service")
    assert result == frozenset({"alice-host", "bob-service"})


def test_parse_drops_short_identifiers() -> None:
    # MIN_IDENTIFIER_LENGTH is 4, so "abc" (3 chars) is dropped.
    result = parse_identifier_set("abc alice-host")
    assert result == frozenset({"alice-host"})


def test_parse_keeps_min_length_identifier() -> None:
    # MIN_IDENTIFIER_LENGTH is 4: exactly 4 chars is the boundary — must pass.
    # An off-by-one (>= → >) would silently drop all 4-char hostnames.
    assert parse_identifier_set("abcd") == frozenset({"abcd"})


# ── scan_text ────────────────────────────────────────────────────────────────


def test_scan_text_finds_substring() -> None:
    violations = list(scan_text("the admin at alice-host logged in", frozenset({"alice-host"})))
    assert len(violations) == 1
    assert violations[0].identifier == "alice-host"
    assert violations[0].line_number == 1
    assert "alice-host" in violations[0].line


def test_scan_text_case_insensitive() -> None:
    violations = list(scan_text("ALICE-HOST alice-host Alice-Host", frozenset({"alice-host"})))
    assert len(violations) == 3


def test_scan_text_multiple_identifiers() -> None:
    text = "alice-host and bob-service both appear"
    violations = list(scan_text(text, frozenset({"alice-host", "bob-service"})))
    assert len(violations) == 2
    ids = {v.identifier for v in violations}
    assert ids == {"alice-host", "bob-service"}


def test_scan_text_no_identifiers_no_violations() -> None:
    assert list(scan_text("some text", frozenset())) == []


def test_scan_text_multiple_occurrences_on_same_line() -> None:
    violations = list(scan_text("alice-host alice-host alice-host", frozenset({"alice-host"})))
    assert len(violations) == 3


def test_scan_text_tracks_line_numbers() -> None:
    text = "line one\nalice-host here\nline three\nbob-service here"
    violations = list(scan_text(text, frozenset({"alice-host", "bob-service"})))
    assert len(violations) == 2
    assert violations[0].line_number == 2
    assert violations[1].line_number == 4


def test_scan_text_matches_inside_longer_tokens() -> None:
    # The docstring says identifiers can appear inside longer tokens.
    violations = list(scan_text("xalice-hosty", frozenset({"alice-host"})))
    assert len(violations) == 1


def test_scan_text_empty_text() -> None:
    assert list(scan_text("", frozenset({"alice-host"}))) == []


def test_scan_text_short_identifiers_filtered() -> None:
    # scan_text also applies _filter_identifiers, so short tokens are dropped.
    assert list(scan_text("abc abc", frozenset({"abc"}))) == []


def test_scan_text_overlapping_identifiers_both_match() -> None:
    # A denylist containing both a prefix and a longer variant (e.g. "svc-da"
    # and "svc-da-prod") yields two violations for the same position — both
    # identifiers are present. This pins the current behavior.
    violations = list(scan_text("alice-host", frozenset({"alice", "alice-host"})))
    assert len(violations) == 2
    assert {v.identifier for v in violations} == {"alice", "alice-host"}


# ── _sniff_encoding ──────────────────────────────────────────────────────────


def test_sniff_utf16_le_bom() -> None:
    assert _sniff_encoding(b"\xff\xfehello") == "utf-16-le"


def test_sniff_utf16_be_bom() -> None:
    assert _sniff_encoding(b"\xfe\xffhello") == "utf-16-be"


def test_sniff_utf8_bom() -> None:
    assert _sniff_encoding(b"\xef\xbb\xbfhello") == "utf-8-sig"


def test_sniff_no_bom_returns_none() -> None:
    assert _sniff_encoding(b"hello world") is None


def test_sniff_empty_chunk_returns_none() -> None:
    assert _sniff_encoding(b"") is None


def test_sniff_partial_bom_returns_none() -> None:
    # Only 2 of the 3 UTF-8 BOM bytes — not a valid BOM.
    assert _sniff_encoding(b"\xef\xbb") is None


# ── _is_binary ───────────────────────────────────────────────────────────────


def test_is_binary_null_byte_is_binary() -> None:
    assert _is_binary(b"hello\x00world") is True


def test_is_binary_plain_text_is_not_binary() -> None:
    assert _is_binary(b"hello world") is False


def test_is_binary_utf16_le_bom_not_binary() -> None:
    # UTF-16-LE text contains null bytes for ASCII chars, but the BOM
    # overrides the null-byte heuristic.
    assert _is_binary(b"\xff\xfeh\x00e\x00l\x00l\x00o\x00") is False


def test_is_binary_utf16_be_bom_not_binary() -> None:
    assert _is_binary(b"\xfe\xff\x00h\x00e\x00l\x00l\x00o") is False


def test_is_binary_utf8_bom_not_binary() -> None:
    assert _is_binary(b"\xef\xbb\xbfhello") is False


def test_is_binary_empty_chunk_not_binary() -> None:
    assert _is_binary(b"") is False


# ── scan_files ───────────────────────────────────────────────────────────────


def test_scan_files_finds_identifier_in_text_file(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("the admin at alice-host logged in\n")
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert len(violations) == 1
    assert violations[0].identifier == "alice-host"
    assert violations[0].path == f
    assert violations[0].line_number == 1


def test_scan_files_skips_binary_files(tmp_path: Path) -> None:
    f = tmp_path / "binary.bin"
    f.write_bytes(b"alice-host\x00\x01\x02\x03")
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert violations == []


def test_scan_files_reads_utf8_bom_file(tmp_path: Path) -> None:
    f = tmp_path / "bom.txt"
    f.write_bytes(b"\xef\xbb\xbfthe admin at alice-host logged in\n")
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert len(violations) == 1


def test_scan_files_reads_utf16_le_file(tmp_path: Path) -> None:
    f = tmp_path / "utf16.txt"
    content = "the admin at alice-host logged in\n"
    f.write_bytes(b"\xff\xfe" + content.encode("utf-16-le"))
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert len(violations) == 1
    assert not violations[0].line.startswith("\ufeff"), "BOM must not leak into line"


def test_scan_files_reads_utf16_be_file(tmp_path: Path) -> None:
    f = tmp_path / "utf16be.txt"
    content = "the admin at alice-host logged in\n"
    f.write_bytes(b"\xfe\xff" + content.encode("utf-16-be"))
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert len(violations) == 1
    assert not violations[0].line.startswith("\ufeff"), "BOM must not leak into line"


def test_scan_files_utf8_bom_stripped(tmp_path: Path) -> None:
    f = tmp_path / "bom_utf8.txt"
    content = "alice-host here\n"
    f.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert len(violations) == 1
    assert not violations[0].line.startswith("\ufeff"), "BOM must not leak into line"


def test_scan_files_identifier_at_start_of_utf16_file(tmp_path: Path) -> None:
    # Identifier at position 0 after BOM — the most sensitive case for BOM
    # leakage into the reported line.
    f = tmp_path / "utf16_start.txt"
    content = "alice-host is here\n"
    f.write_bytes(b"\xff\xfe" + content.encode("utf-16-le"))
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert len(violations) == 1
    assert violations[0].line.startswith("alice-host"), "line should start with identifier, not BOM"


def test_scan_files_no_identifier_no_violations(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("nothing relevant here\n")
    assert scan_files(frozenset({"alice-host"}), [f]) == []


def test_scan_files_multiple_files(tmp_path: Path) -> None:
    f1 = tmp_path / "a.md"
    f1.write_text("alice-host appears here\n")
    f2 = tmp_path / "b.md"
    f2.write_text("nothing here\n")
    f3 = tmp_path / "c.md"
    f3.write_text("bob-service appears here\n")
    violations = scan_files(frozenset({"alice-host", "bob-service"}), [f1, f2, f3])
    assert len(violations) == 2
    paths = {v.path for v in violations}
    assert paths == {f1, f3}


def test_scan_files_skips_unreadable_file_gracefully(tmp_path: Path) -> None:
    # Use a directory (which can't be opened with open()) to simulate an
    # unreadable path — OSError is caught and the file is skipped.
    d = tmp_path / "not_a_file"
    d.mkdir()
    violations = scan_files(frozenset({"alice-host"}), [d])
    assert violations == []


def test_scan_files_empty_path_list() -> None:
    assert scan_files(frozenset({"alice-host"}), []) == []


def test_scan_files_sets_path_on_violation(tmp_path: Path) -> None:
    f = tmp_path / "doc.md"
    f.write_text("alice-host here\n")
    violations = scan_files(frozenset({"alice-host"}), [f])
    assert violations[0].path == f


# ── leaked_tracked_files ─────────────────────────────────────────────────────


def test_leaked_tracked_files_detects_samples_root() -> None:
    paths = [Path("samples/secret.env"), Path("src/main.py")]
    leaked = leaked_tracked_files(paths, frozenset({"samples"}))
    assert leaked == [Path("samples/secret.env")]


def test_leaked_tracked_files_ignores_nested_samples() -> None:
    # tests/samples/ is a legitimate code dir, not the guarded root samples/.
    paths = [Path("tests/samples/data.txt"), Path("src/main.py")]
    leaked = leaked_tracked_files(paths, frozenset({"samples"}))
    assert leaked == []


def test_leaked_tracked_files_empty_input() -> None:
    assert leaked_tracked_files([], frozenset({"samples"})) == []


def test_leaked_tracked_files_multiple_guarded() -> None:
    paths = [
        Path("samples/a.txt"),
        Path("other/b.txt"),
        Path("samples/c.txt"),
    ]
    leaked = leaked_tracked_files(paths, frozenset({"samples"}))
    assert leaked == [Path("samples/a.txt"), Path("samples/c.txt")]


# ── Violation dataclass ──────────────────────────────────────────────────────


def test_violation_is_frozen() -> None:
    v = Violation(identifier="x", path=Path("a"), line_number=1, line="text")
    with pytest.raises(AttributeError):
        v.identifier = "y"  # type: ignore[misc]


# ── main() integration ──────────────────────────────────────────────────────


def test_main_leaked_samples_dir_returns_1(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The always-on samples/ guard must fail even when the forbidden-identifier
    secret is unset. This is the security-critical path: a ``git add -f
    samples/secrets.env`` must fail CI regardless of configuration."""
    monkeypatch.delenv("VITRINE_FORBIDDEN_IDENTIFIERS", raising=False)
    monkeypatch.setattr(
        _mod, "collect_tracked_paths", lambda: [Path("samples/leaked.env")]
    )
    assert main([]) == 1


def test_main_no_secret_no_leaks_returns_0(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Without the forbidden-identifier secret, clean repo passes (exit 0)."""
    monkeypatch.delenv("VITRINE_FORBIDDEN_IDENTIFIERS", raising=False)
    monkeypatch.setattr(_mod, "collect_tracked_paths", lambda: [Path("src/main.py")])
    assert main([]) == 0


def test_main_with_identifiers_finds_violation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """With identifiers set, a file containing one is flagged (exit 1)."""
    f = tmp_path / "doc.md"
    f.write_text("the admin at alice-host logged in\n")
    monkeypatch.setenv("VITRINE_FORBIDDEN_IDENTIFIERS", "alice-host")
    monkeypatch.setattr(_mod, "collect_tracked_paths", lambda: [f])
    assert main([]) == 1


def test_main_with_identifiers_clean_file_returns_0(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """With identifiers set, a clean file passes (exit 0)."""
    f = tmp_path / "doc.md"
    f.write_text("nothing relevant here\n")
    monkeypatch.setenv("VITRINE_FORBIDDEN_IDENTIFIERS", "alice-host")
    monkeypatch.setattr(_mod, "collect_tracked_paths", lambda: [f])
    assert main([]) == 0


def test_main_empty_secret_skips_scan(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Empty secret string skips the scan (exit 0) — no-op for fresh clones."""
    f = tmp_path / "doc.md"
    f.write_text("alice-host here\n")
    monkeypatch.setenv("VITRINE_FORBIDDEN_IDENTIFIERS", "   ")
    monkeypatch.setattr(_mod, "collect_tracked_paths", lambda: [f])
    assert main([]) == 0


def test_main_short_identifiers_skipped(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """If all identifiers are below MIN_IDENTIFIER_LENGTH, the scan is skipped."""
    f = tmp_path / "doc.md"
    f.write_text("abc abc abc\n")
    monkeypatch.setenv("VITRINE_FORBIDDEN_IDENTIFIERS", "abc")
    monkeypatch.setattr(_mod, "collect_tracked_paths", lambda: [f])
    assert main([]) == 0