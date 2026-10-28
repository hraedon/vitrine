"""Real cooperating processes preserve complete publications on Windows and POSIX."""

import os
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest

from vitrine.publish import OutputError, staged_directory


def _wait_for(path: Path, child: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 15
    while not path.exists():
        if child.poll() is not None or time.monotonic() > deadline:
            stdout, stderr = child.communicate(timeout=2)
            pytest.fail(f"publisher did not reach {path.name}: {stdout} {stderr}")
        time.sleep(0.01)


def test_processes_wait_for_one_output_root_and_publish_whole_trees(tmp_path: Path) -> None:
    output = tmp_path / "output"
    script = """
import sys
from pathlib import Path
from vitrine.publish import staged_directory
root = Path(sys.argv[1])
(root / 'started').touch()
with staged_directory(root / 'output') as staging:
    (root / 'entered').touch()
    (staging / 'second.txt').write_text('second', encoding='utf-8')
"""
    with staged_directory(output) as staging:
        (staging / "first.txt").write_text("first", encoding="utf-8")
        child = subprocess.Popen(
            [sys.executable, "-c", script, str(tmp_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            _wait_for(tmp_path / "started", child)
            # The first publisher owns the lock, so the second cannot enter
            # regardless of how quickly its interpreter started.
            with pytest.raises(subprocess.TimeoutExpired):
                child.wait(timeout=0.2)
            assert not (tmp_path / "entered").exists()
        except BaseException:
            child.kill()
            child.communicate(timeout=5)
            raise
    try:
        stdout, stderr = child.communicate(timeout=15)
        assert child.returncode == 0, (stdout, stderr)
        assert sorted(path.name for path in output.iterdir()) == ["second.txt"]
        assert (output / "second.txt").read_text(encoding="utf-8") == "second"
    finally:
        if child.poll() is None:
            child.kill()
            child.communicate(timeout=5)


def test_abrupt_process_exit_releases_lock_and_next_writer_cleans_partial_tree(
    tmp_path: Path,
) -> None:
    script = """
import os
import sys
from pathlib import Path
from vitrine.publish import staged_directory
with staged_directory(Path(sys.argv[1])) as staging:
    (staging / 'unfinished.txt').write_text('partial', encoding='utf-8')
    os._exit(23)
"""
    output = tmp_path / "output"
    result = subprocess.run([sys.executable, "-c", script, str(output)], timeout=15)
    assert result.returncode == 23
    assert not output.exists()
    assert list(tmp_path.glob(".output.staging-*"))
    with staged_directory(output) as staging:
        (staging / "complete.txt").write_text("finished", encoding="utf-8")
    assert sorted(path.name for path in output.iterdir()) == ["complete.txt"]
    assert not list(tmp_path.glob(".output.staging-*"))


def test_build_and_coverage_work_with_a_legacy_console_encoding(tmp_path: Path) -> None:
    """Default Windows-style text settings must not corrupt site bytes."""
    root = Path(__file__).parent.parent
    destination = tmp_path / "site-展示"
    env = dict(os.environ, PYTHONUTF8="0", PYTHONIOENCODING="cp1252")
    for arguments in (["build", "--out", str(destination)],
                      ["check", "--against-build", str(destination)],
                      ["export", "--out", str(tmp_path / "export-展示")]):
        result = subprocess.run(
            [sys.executable, "-m", "vitrine.cli", *arguments],
            cwd=root, env=env, capture_output=True, timeout=60,
        )
        assert result.returncode == 0, (result.stdout, result.stderr)
    for path in destination.rglob("*"):
        if path.is_file():
            raw = path.read_bytes()
            raw.decode("utf-8")
            if path.suffix in {".html", ".css", ".js", ".txt", ".json"}:
                assert b"\r\n" not in raw, path


@pytest.mark.skipif(os.name != "nt", reason="Windows DOS read-only cleanup")
def test_previous_readonly_output_does_not_strand_a_backup(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    previous = output / "previous.txt"
    previous.write_text("old", encoding="utf-8")
    previous.chmod(stat.S_IREAD)
    for content in ("new", "newer"):
        with staged_directory(output) as staging:
            (staging / "current.txt").write_text(content, encoding="utf-8")
        assert (output / "current.txt").read_text(encoding="utf-8") == content
        assert not list(tmp_path.glob(".output.backup-*"))


@pytest.mark.skipif(os.name != "nt", reason="Windows directory junctions")
@pytest.mark.parametrize("position", ["destination", "ancestor", "existing-tree"])
def test_junctions_cannot_redirect_publication(tmp_path: Path, position: str) -> None:
    target = tmp_path / "outside"
    target.mkdir()
    sentinel = target / "keep.txt"
    sentinel.write_text("keep", encoding="utf-8")
    output = tmp_path / "output"
    if position == "existing-tree":
        output.mkdir()
        junction = output / "redirect"
        destination = output
    else:
        junction = output
        destination = output / "nested" if position == "ancestor" else output
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    try:
        with pytest.raises(OutputError, match="symlink"), staged_directory(destination):
            pytest.fail("junction was accepted")
        assert sentinel.read_text(encoding="utf-8") == "keep"
        assert sorted(path.name for path in target.iterdir()) == ["keep.txt"]
    finally:
        junction.rmdir()  # Remove the junction itself; never traverse its target.
