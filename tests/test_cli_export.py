"""CLI, custom-path, citation, and publication-rollback coverage."""

import os
import stat
import threading
from pathlib import Path

import pytest

from vitrine.cli import main
from vitrine.publish import (
    OutputError,
    copy_existing_tree,
    ensure_publishable_directory,
    staged_directory,
)

REPO_ROOT = Path(__file__).parent.parent


def _minimal_data(root: Path) -> Path:
    root.mkdir(parents=True)
    (root / "sources.toml").write_text(
        '[[source]]\nid = "src-1"\ntitle = "T"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "all families"\n'
    )
    (root / "assumptions.toml").write_text(
        '[[assumption]]\nid = "composite-family"\ntitle = "A"\nstatement = "S"\n'
    )
    room = root / "us"
    room.mkdir()
    (room / "1950s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n'
        '[[fact]]\nid = "us-1950s-x"\npanel = "budget"\nlabel = "L"\nvalue = "12%"\n'
        'unit = "%"\nsource = "src-1"\ntier = "A"\nquantity = 12\n'
    )
    return root


def _export_args(data: Path, output: Path) -> list[str]:
    return ["--data", str(data), "export", "--out", str(output)]


def test_export_cli_honors_custom_paths_and_citation_surface(tmp_path: Path) -> None:
    data = _minimal_data(tmp_path / "custom-data")
    output = tmp_path / "nested" / "custom-build"

    assert main(_export_args(data, output)) == 0
    assert (output / "data" / "corpus.json").is_file()
    assert (output / "data" / "facts.csv").is_file()
    assert (output / "data" / "facts-raw.csv").is_file()
    page = (output / "data.html").read_text()
    assert "<nav" not in page
    assert 'href="index.html"' not in page
    assert 'href="data/corpus.json"' in page
    assert "CC BY-SA 4.0" in page
    for relative in (
        "assets/enhancements.js",
        "assets/museum.css",
        "data/corpus.json",
        "data/facts.csv",
        "data/facts-raw.csv",
    ):
        assert (output / relative).is_file()

    # Export is a surface update, not a reason to discard an existing full site.
    (output / "keep.txt").write_text("preserve")
    assert main(_export_args(data, output)) == 0
    assert (output / "keep.txt").read_text() == "preserve"


def test_subsequent_export_preserves_navigation_for_essay_free_full_shape(
    tmp_path: Path,
) -> None:
    data = _minimal_data(tmp_path / "custom-data")
    output = tmp_path / "full-build"
    for relative in (
        "index.html",
        "corridors/index.html",
        "affordability/index.html",
        "walkthrough.html",
        "methodology.html",
        "bibliography.html",
    ):
        page = output / relative
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("existing full-build page")

    assert main(_export_args(data, output)) == 0
    page = (output / "data.html").read_text()
    assert '<nav class="museum-map"' in page
    assert 'href="index.html">Rooms</a>' in page
    assert 'href="methodology.html">Method</a>' in page
    assert 'href="data.html">Data</a>' in page
    assert "essays/index.html" not in page


def test_citation_file_scopes_the_corpus_license() -> None:
    citation = (REPO_ROOT / "CITATION.cff").read_text()
    assert "title: \"vitrine corpus\"" in citation
    assert "type: dataset" in citation
    assert "license: CC-BY-SA-4.0" in citation
    assert "exporter software is" in citation
    assert "If you use the vitrine corpus" in citation


def test_export_rejects_symlinked_destination(tmp_path: Path) -> None:
    data = _minimal_data(tmp_path / "data")
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "published"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("the platform does not support directory symlinks")

    assert main(_export_args(data, link)) == 1
    assert not (target / "data").exists()


def test_export_rejects_output_source_path_overlap(tmp_path: Path) -> None:
    data = _minimal_data(tmp_path / "data")
    for output in (data, data / "nested-output", tmp_path):
        assert main(_export_args(data, output)) == 1


def test_build_rejects_output_source_path_overlap(tmp_path: Path) -> None:
    data = _minimal_data(tmp_path / "data")
    for output in (data, data / "nested-output", tmp_path):
        assert main(["--data", str(data), "build", "--out", str(output)]) == 1


def test_existing_symlink_in_destination_is_rejected(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("do not read")
    link = output / "escape"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("the platform does not support symlinks")

    with pytest.raises(OutputError, match="symlink inside output"), staged_directory(
        output
    ) as staging:
        copy_existing_tree(output, staging)

    assert outside.read_text() == "do not read"
    assert link.is_symlink()


def test_export_failure_rolls_back_existing_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = _minimal_data(tmp_path / "data")
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")

    import vitrine.site.build as site_build

    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("landing page failed")

    monkeypatch.setattr(site_build, "build_data_page", fail)
    with pytest.raises(RuntimeError, match="landing page failed"):
        main(_export_args(data, output))

    assert (output / "sentinel.txt").read_text() == "old"
    assert not (output / "data").exists()
    assert not list(tmp_path.glob(".output.staging-*"))


def test_staging_writer_failure_leaves_destination_unchanged(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")

    with pytest.raises(RuntimeError, match="interrupted"), staged_directory(output) as staging:
        (staging / "partial.txt").write_text("new")
        raise RuntimeError("interrupted")

    assert (output / "sentinel.txt").read_text() == "old"
    assert not (output / "partial.txt").exists()
    assert not list(tmp_path.glob(".output.staging-*"))


def test_build_failure_rolls_back_existing_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = _minimal_data(tmp_path / "data")
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")

    import vitrine.site.build as site_build

    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("render failed")

    monkeypatch.setattr(site_build, "_build_site_contents", fail)
    with pytest.raises(RuntimeError, match="render failed"):
        main(["--data", str(data), "build", "--out", str(output)])

    assert (output / "sentinel.txt").read_text() == "old"
    assert not list(tmp_path.glob(".output.staging-*"))


def test_publish_swap_failure_restores_existing_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")

    import vitrine.publish as publish

    real_replace = publish.os.replace

    def fail_swap(source: str | Path, destination: str | Path) -> None:
        if Path(source).name.startswith(".output.staging-") and Path(destination) == output:
            raise OSError("swap failed")
        real_replace(source, destination)

    monkeypatch.setattr(publish.os, "replace", fail_swap)
    with pytest.raises(OutputError, match="previous destination was restored"), staged_directory(
        output
    ) as staging:
        (staging / "new.txt").write_text("new")

    assert (output / "sentinel.txt").read_text() == "old"
    assert not (output / "new.txt").exists()
    assert not list(tmp_path.glob(".output.staging-*"))
    assert not list(tmp_path.glob(".output.backup-*"))


def test_publish_rollback_failure_leaves_backup_for_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")

    import vitrine.publish as publish

    real_replace = publish.os.replace

    def fail_install_and_restore(source: str | Path, destination: str | Path) -> None:
        source_path = Path(source)
        if Path(destination) == output and (
            source_path.name.startswith(".output.staging-")
            or source_path.name.startswith(".output.backup-")
        ):
            raise OSError("rollback path failed")
        real_replace(source, destination)

    monkeypatch.setattr(publish.os, "replace", fail_install_and_restore)
    with pytest.raises(OutputError, match="rollback also failed") as raised, staged_directory(
        output
    ) as staging:
        (staging / "new.txt").write_text("new")

    assert "destination may be absent" in str(raised.value)
    assert "backup remains at" in str(raised.value)
    assert not output.exists()
    backups = list(tmp_path.glob(".output.backup-*"))
    assert len(backups) == 1
    assert (backups[0] / "sentinel.txt").read_text() == "old"
    assert not list(tmp_path.glob(".output.staging-*"))


def test_publish_backup_cleanup_failure_keeps_new_tree_and_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")

    import vitrine.publish as publish

    real_remove_tree = publish._remove_tree

    def fail_backup_cleanup(path: Path) -> None:
        if path.name.startswith(".output.backup-"):
            raise OSError("backup cleanup failed")
        real_remove_tree(path)

    monkeypatch.setattr(publish, "_remove_tree", fail_backup_cleanup)
    with (
        pytest.raises(OutputError, match="backup cleanup failed"),
        staged_directory(output) as staging,
    ):
        (staging / "new.txt").write_text("new")

    assert (output / "new.txt").read_text() == "new"
    assert not (output / "sentinel.txt").exists()
    assert len(list(tmp_path.glob(".output.backup-*"))) == 1
    assert not list(tmp_path.glob(".output.staging-*"))


def test_publish_cleanup_artifact_with_destination_fails_closed(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "new.txt").write_text("new")
    backup = tmp_path / ".output.backup-cleanup"
    backup.mkdir()
    (backup / "old.txt").write_text("old")

    with pytest.raises(OutputError, match="require inspection"), staged_directory(output):
        pass

    assert (output / "new.txt").read_text() == "new"
    assert (backup / "old.txt").read_text() == "old"


@pytest.mark.parametrize("name", ["out[abc]", "out*name", "out?name"])
def test_rollback_discovery_treats_output_name_as_literal(
    tmp_path: Path, name: str
) -> None:
    output = tmp_path / name
    backup = tmp_path / f".{name}.backup-crash"
    backup.mkdir()
    (backup / "sentinel.txt").write_text("old")

    with staged_directory(output) as staging:
        (staging / "new.txt").write_text("new")

    assert (output / "new.txt").read_text() == "new"
    assert not backup.exists()


def test_preexisting_publication_lock_symlink_is_rejected(tmp_path: Path) -> None:
    output = tmp_path / "output"
    outside = tmp_path / "outside"
    outside.mkdir()
    lock = tmp_path / ".output.publish.lock"
    try:
        lock.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("the platform does not support directory symlinks")

    with pytest.raises(OutputError, match="publication lock"), staged_directory(output):
        pass

    assert not output.exists()


def test_cooperating_publishers_are_serialized(tmp_path: Path) -> None:
    output = tmp_path / "output"
    first_entered = threading.Event()
    second_started = threading.Event()
    second_entered = threading.Event()
    release_first = threading.Event()
    errors: list[BaseException] = []

    def first_writer() -> None:
        try:
            with staged_directory(output) as staging:
                (staging / "first.txt").write_text("first")
                first_entered.set()
                assert release_first.wait(timeout=5)
        except BaseException as exc:  # pragma: no cover - reported below
            errors.append(exc)

    def second_writer() -> None:
        try:
            assert first_entered.wait(timeout=5)
            second_started.set()
            with staged_directory(output) as staging:
                second_entered.set()
                (staging / "second.txt").write_text("second")
        except BaseException as exc:  # pragma: no cover - reported below
            errors.append(exc)

    first = threading.Thread(target=first_writer)
    second = threading.Thread(target=second_writer)
    first.start()
    assert first_entered.wait(timeout=5)
    second.start()
    assert second_started.wait(timeout=5)
    assert not second_entered.wait(timeout=0.2)
    release_first.set()
    first.join(timeout=5)
    second.join(timeout=5)

    assert not first.is_alive()
    assert not second.is_alive()
    assert not errors
    assert (output / "second.txt").read_text() == "second"


def test_nested_surface_reuses_output_root_lock_without_nested_artifact(
    tmp_path: Path,
) -> None:
    output = tmp_path / "output"
    with (
        staged_directory(output) as staging,
        staged_directory(staging / "data", lock_root=output) as data_staging,
    ):
        (data_staging / "corpus.json").write_text("{}")

    assert (output / "data" / "corpus.json").read_text() == "{}"
    assert not list(output.rglob("*.publish.lock"))


def test_orphan_staging_artifact_is_cleaned_by_next_cooperating_run(
    tmp_path: Path,
) -> None:
    output = tmp_path / "output"
    orphan = tmp_path / ".output.staging-orphan"
    orphan.mkdir()
    (orphan / "partial.txt").write_text("partial")

    with staged_directory(output) as staging:
        (staging / "new.txt").write_text("new")

    assert not orphan.exists()
    assert (output / "new.txt").read_text() == "new"


def test_published_directories_are_readable_and_traversable_under_umask(
    tmp_path: Path,
) -> None:
    for requested_umask, expected_mode in ((0o027, 0o755), (0o777, 0o755)):
        previous_umask = os.umask(requested_umask)
        try:
            output = tmp_path / f"output-{requested_umask:o}"
            with staged_directory(output) as staging:
                nested = staging / "data"
                nested.mkdir(mode=0o755)
                ensure_publishable_directory(nested)
                (nested / "index.html").write_text("ok")
                executable = staging / "legacy-script.js"
                executable.write_text("not executable in a static tree")
                os.chmod(executable, 0o755)
                assert stat.S_IMODE(staging.stat().st_mode) == expected_mode
                assert stat.S_IMODE(nested.stat().st_mode) == expected_mode

            assert stat.S_IMODE(output.stat().st_mode) == expected_mode
            assert stat.S_IMODE((output / "data").stat().st_mode) == expected_mode
            assert stat.S_IMODE((output / "data" / "index.html").stat().st_mode) == 0o644
            assert stat.S_IMODE((output / "legacy-script.js").stat().st_mode) == 0o644
        finally:
            os.umask(previous_umask)


def test_nested_publications_repeat_under_umask_0777(tmp_path: Path) -> None:
    previous_umask = os.umask(0o777)
    try:
        existing_parent_mode = stat.S_IMODE(tmp_path.stat().st_mode)
        output = tmp_path / "fresh-parent" / "nested" / "output"
        for content in ("first", "second"):
            with staged_directory(output) as staging:
                (staging / "index.html").write_text(content)

        assert (output / "index.html").read_text() == "second"
        assert stat.S_IMODE((output.parent.parent).stat().st_mode) == 0o755
        assert stat.S_IMODE(output.parent.stat().st_mode) == 0o755
        assert stat.S_IMODE(tmp_path.stat().st_mode) == existing_parent_mode
        assert stat.S_IMODE(output.stat().st_mode) == 0o755
        assert stat.S_IMODE((output / "index.html").stat().st_mode) == 0o644
        lock = output.parent / ".output.publish.lock"
        assert stat.S_IMODE(lock.stat().st_mode) == 0o600
    finally:
        os.umask(previous_umask)


def test_existing_private_parent_mode_is_preserved_under_both_umasks(
    tmp_path: Path,
) -> None:
    private_parent = tmp_path / "private"
    private_parent.mkdir(mode=0o700)
    os.chmod(private_parent, 0o700)
    for requested_umask in (0o022, 0o777):
        previous_umask = os.umask(requested_umask)
        try:
            output = private_parent / f"output-{requested_umask:o}"
            with staged_directory(output) as staging:
                (staging / "index.html").write_text("ok")
        finally:
            os.umask(previous_umask)

        assert stat.S_IMODE(private_parent.stat().st_mode) == 0o700
        assert stat.S_IMODE(output.stat().st_mode) == 0o755
        assert stat.S_IMODE((output / "index.html").stat().st_mode) == 0o644


def test_nested_exports_repeat_under_umask_0777(tmp_path: Path) -> None:
    data = _minimal_data(tmp_path / "data")
    output = tmp_path / "fresh-parent" / "nested" / "output"
    previous_umask = os.umask(0o777)
    try:
        assert main(_export_args(data, output)) == 0
        assert main(_export_args(data, output)) == 0
    finally:
        os.umask(previous_umask)

    assert stat.S_IMODE(output.stat().st_mode) == 0o755
    assert stat.S_IMODE((output / "data").stat().st_mode) == 0o755
    assert stat.S_IMODE((output / "data" / "corpus.json").stat().st_mode) == 0o644
    assert stat.S_IMODE((output.parent / ".output.publish.lock").stat().st_mode) == 0o600


def test_export_removes_legacy_nested_lock_and_staging_artifacts(
    tmp_path: Path,
) -> None:
    data = _minimal_data(tmp_path / "data")
    output = tmp_path / "output"
    output.mkdir()
    (output / ".data.publish.lock").write_text("legacy lock")
    user_lock = output / "user.publish.lock"
    user_lock.write_text("user lock")
    nested_user_lock = output / "nested" / ".data.publish.lock"
    nested_user_lock.parent.mkdir()
    nested_user_lock.write_text("nested user lock")
    orphan = output / ".data.staging-orphan"
    orphan.mkdir()
    (orphan / "partial.txt").write_text("partial")

    assert main(_export_args(data, output)) == 0
    assert not (output / ".data.publish.lock").exists()
    assert user_lock.read_text() == "user lock"
    assert nested_user_lock.read_text() == "nested user lock"
    assert not orphan.exists()


def test_cli_wraps_publication_oserror_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    data = _minimal_data(tmp_path / "data")
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")

    import vitrine.publish as publish

    real_replace = publish.os.replace

    def fail_install(source: str | Path, destination: str | Path) -> None:
        if Path(source).name.startswith(".output.staging-") and Path(destination) == output:
            raise OSError("swap failed")
        real_replace(source, destination)

    monkeypatch.setattr(publish.os, "replace", fail_install)
    assert main(_export_args(data, output)) == 1

    captured = capsys.readouterr()
    assert "OUTPUT ERROR:" in captured.err
    assert "previous destination was restored" in captured.err
    assert "Traceback" not in captured.err
    assert (output / "sentinel.txt").read_text() == "old"


def test_interrupted_swap_recovers_one_rollback_artifact(tmp_path: Path) -> None:
    output = tmp_path / "output"
    output.mkdir()
    (output / "sentinel.txt").write_text("old")
    rollback = tmp_path / ".output.backup-crash"
    os.replace(output, rollback)

    with staged_directory(output) as staging:
        (staging / "new.txt").write_text("new")

    assert (output / "new.txt").read_text() == "new"
    assert not rollback.exists()


def test_ambiguous_rollback_artifacts_fail_closed(tmp_path: Path) -> None:
    output = tmp_path / "output"
    first = tmp_path / ".output.backup-one"
    second = tmp_path / ".output.backup-two"
    first.mkdir()
    second.mkdir()

    with pytest.raises(OutputError, match="ambiguous rollback"), staged_directory(output):
        pass

    assert first.is_dir()
    assert second.is_dir()
    assert not output.exists()
