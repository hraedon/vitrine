"""Freshness must detect content changes even when exhibit IDs stay fixed."""

from __future__ import annotations

import functools
import http.server
import threading
from collections.abc import Iterator
from pathlib import Path

import check_deploy_freshness as freshness
import pytest


@pytest.fixture
def deployment(tmp_path: Path) -> Iterator[tuple[Path, Path, str]]:
    built = tmp_path / "built"
    served = tmp_path / "served"
    # A mount prefix and an escaped filename exercise URL construction too.
    live = served / "museum"
    for root in (built, live):
        for name, content in {
            "index.html": b"<h1>Museum</h1>",
            "facts-manifest.txt": b"us-1950s-example\n",
            "rooms/us-1950s.html": b"<p>Value and citation</p>",
            "assets/museum.css": b"body { color: black; }",
            "assets/room guide.js": b"'use strict';",
            "data/corpus.json": b'{"facts": []}',
        }.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(served))
    with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield built, live, f"http://127.0.0.1:{server.server_port}/museum/"
        finally:
            server.shutdown()
            thread.join()


def test_exact_deployment_matches(deployment: tuple[Path, Path, str]) -> None:
    built, _, url = deployment
    assert freshness.compare_site(built, url) == 0


@pytest.mark.parametrize("artifact", [
    "rooms/us-1950s.html", "assets/museum.css", "assets/room guide.js", "data/corpus.json",
])
def test_same_identifiers_do_not_hide_content_drift(
    deployment: tuple[Path, Path, str], artifact: str, capsys: pytest.CaptureFixture[str],
) -> None:
    built, live, url = deployment
    (live / artifact).write_bytes(b"stale")
    assert (built / "facts-manifest.txt").read_bytes() == (
        live / "facts-manifest.txt"
    ).read_bytes()
    assert freshness.compare_site(built, url) == 1
    assert f"DIFFERENT: {artifact}" in capsys.readouterr().out


def test_extra_response_bytes_are_not_a_match(deployment: tuple[Path, Path, str]) -> None:
    built, live, url = deployment
    with (live / "index.html").open("ab") as output:
        output.write(b" extra")
    assert freshness.compare_site(built, url) == 1


def test_missing_remote_artifact_is_unavailable(deployment: tuple[Path, Path, str]) -> None:
    built, live, url = deployment
    (live / "assets/museum.css").unlink()
    assert freshness.compare_site(built, url) == 2


def test_incomplete_local_build_is_rejected(tmp_path: Path) -> None:
    assert freshness.compare_site(tmp_path, "http://127.0.0.1:1") == 2


def test_legacy_match_does_not_claim_content_freshness(
    deployment: tuple[Path, Path, str], monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    built, live, url = deployment
    (live / "index.html").write_text("stale presentation", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["check", str(built / "facts-manifest.txt"), "--url", url])
    assert freshness.main() == 0
    output = capsys.readouterr().out
    assert "ID MATCH:" in output
    assert "FRESH:" not in output


def test_directory_cli_checks_content(
    deployment: tuple[Path, Path, str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    built, live, url = deployment
    (live / "index.html").write_text("stale presentation", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["check", str(built), "--url", url])
    assert freshness.main() == 1
