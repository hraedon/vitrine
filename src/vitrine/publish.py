"""Safe publication helpers for generated output directories.

Builders render into a sibling staging directory and publish the completed
directory with same-filesystem ``os.replace`` operations. The destination is
never written file-by-file, so a render exception before publication cannot
leave a half-new corpus beside an old landing page. For an existing directory,
portable stdlib APIs require two renames (old → rollback artifact, staging →
destination): readers can observe a brief missing destination during that
handoff, but never a mixture of old and new files.

The failure boundary is deliberately explicit. If installing the new tree
fails, publication attempts to restore the old tree. A failed restore leaves
the destination possibly absent and the named rollback artifact for inspection
or a later unambiguous recovery. If cleanup of the old tree fails after the new
tree is installed, the new tree remains at the destination and the rollback
artifact remains; the operation reports an error rather than claiming that the
old tree is still in place. Recovery only happens when the destination is
absent and exactly one valid artifact is present; a destination plus an
artifact, or several artifacts, fails closed.

The supported CLI threat model is a local, non-adversarial single writer.
Each logical output root has one advisory lock, so direct full-site and data
surface writers cooperate rather than publishing concurrently. The lock owner
removes matching orphan staging directories from known root/nested surfaces
before starting. Path and existing-tree symlinks are rejected, but the
preflight checks are not a no-follow/dir-fd defense against an independent
process that deliberately substitutes symlinks after validation. This module
does not make that stronger security claim.

This is deliberately stdlib-only. The site renderer and the corpus exporter
both use it at their CLI boundary; direct projection functions remain useful
for tests and callers that intentionally own their output directory. Note
that "stdlib-only" here also means POSIX-only: the advisory lock uses
``fcntl``, so the module (and the CLI) does not import on Windows.
"""

from __future__ import annotations

import fcntl
import os
import shutil
import stat
import tempfile
import threading
import uuid
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path


class OutputError(Exception):
    """The requested output destination cannot be published safely."""


_REQUESTED_DIRECTORY_MODE = 0o755
_PUBLISHED_DIRECTORY_MODE = 0o755
_PUBLISHED_FILE_MODE = 0o644
# Before the output-root lock namespace, ``export`` left this exact file beside
# the published ``data/`` surface. No wildcard lock cleanup is safe: users may
# legitimately publish files whose names merely end in ``.publish.lock``.
_KNOWN_NESTED_LOCK_ARTIFACT_NAMES = frozenset({".data.publish.lock"})
_LOCK_STATE = threading.local()


def _lexists(path: Path) -> bool:
    """Return whether *path* exists, including a broken symlink."""
    return os.path.lexists(path)


def _reject_symlink_components(destination: Path) -> None:
    """Reject a symlink at any component of an output path."""
    current = destination
    while True:
        if current.is_symlink():
            raise OutputError(f"refusing symlinked output path component: {current}")
        parent = current.parent
        if parent == current:
            return
        current = parent


def _resolve_for_validation(path: Path) -> Path:
    """Resolve when possible, retaining lexical safety under a locked-down parent."""
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def validate_destination(
    destination: Path, forbidden_paths: Iterable[Path] = ()
) -> None:
    """Reject destinations that could redirect or destroy the source tree.

    This is a preflight check, not a race-free no-follow guarantee. The
    publication boundary revalidates under the cooperative destination lock.
    """
    _reject_symlink_components(destination)
    if _lexists(destination) and not destination.is_dir():
        raise OutputError(f"output destination is not a directory: {destination}")

    resolved = _resolve_for_validation(destination)
    cwd = Path.cwd().resolve()
    if cwd == resolved or cwd.is_relative_to(resolved):
        raise OutputError(
            f"refusing output destination that contains the working tree: {destination}"
        )
    for forbidden in forbidden_paths:
        source = _resolve_for_validation(Path(forbidden))
        if (
            resolved == source
            or resolved.is_relative_to(source)
            or source.is_relative_to(resolved)
        ):
            raise OutputError(
                f"output destination overlaps source path: {destination} and {forbidden}"
            )


def validate_existing_tree(root: Path) -> None:
    """Reject a symlink at *root* or anywhere below an existing tree."""
    if not _lexists(root):
        return
    if root.is_symlink():
        raise OutputError(f"refusing symlink inside output destination: {root}")
    if not root.is_dir():
        return
    for path in root.rglob("*"):
        if path.is_symlink():
            raise OutputError(f"refusing symlink inside output destination: {path}")


def ensure_publishable_directory(path: Path) -> None:
    """Make a published directory readable/traversable for static serving.

    Callers create directories with a requested ``0755`` mode, which the
    kernel masks with the process umask. Publication intentionally restores the
    public read/execute bits afterward, while never granting group/other write.
    """
    if stat.S_IMODE(path.stat().st_mode) != _PUBLISHED_DIRECTORY_MODE:
        os.chmod(path, _PUBLISHED_DIRECTORY_MODE)


def ensure_publishable_file(path: Path) -> None:
    """Make a regular static file owner-readable and public-readable."""
    if stat.S_IMODE(path.stat().st_mode) != _PUBLISHED_FILE_MODE:
        os.chmod(path, _PUBLISHED_FILE_MODE)


def ensure_publishable_tree(root: Path) -> None:
    """Validate a tree and ensure every real directory is publishable."""
    if not _lexists(root):
        return
    if root.is_symlink():
        raise OutputError(f"refusing symlink inside output destination: {root}")
    if not root.is_dir():
        return
    # Repair the root before walking it: an old restrictive-umask tree may not
    # be traversable until its root mode is fixed.
    ensure_publishable_directory(root)
    for path in root.rglob("*"):
        if path.is_symlink():
            raise OutputError(f"refusing symlink inside output destination: {path}")
        if path.is_dir():
            ensure_publishable_directory(path)
        elif path.is_file():
            ensure_publishable_file(path)


def _prepare_output_parent(path: Path) -> None:
    """Create missing output-parent components before opening its lock.

    Existing ancestors are only checked for usability; their private modes are
    never widened. Every component created here is repaired immediately after
    ``mkdir`` so a restrictive umask cannot strand the next component.
    """
    path = Path(path)
    _reject_symlink_components(path)
    if _lexists(path):
        if not path.is_dir():
            raise OutputError(f"output parent is not a directory: {path}")
        # Existing private parents are intentionally left untouched. The
        # current owner can use a 0700 parent; widening it would be surprising.
        return

    missing: list[Path] = []
    current = path
    while not _lexists(current):
        missing.append(current)
        parent = current.parent
        if parent == current:
            raise OutputError(f"could not find an existing ancestor for output parent: {path}")
        current = parent
    _reject_symlink_components(current)
    if not current.is_dir():
        raise OutputError(f"output parent is not a directory: {current}")

    for directory in reversed(missing):
        _reject_symlink_components(directory)
        try:
            directory.mkdir(mode=_REQUESTED_DIRECTORY_MODE)
        except FileExistsError:
            if directory.is_symlink() or not directory.is_dir():
                raise OutputError(f"output parent was replaced: {directory}") from None
        ensure_publishable_directory(directory)


def _new_sibling(directory: Path, prefix: str) -> Path:
    """Reserve a unique, non-existent sibling path for a directory swap."""
    temporary = Path(tempfile.mkdtemp(prefix=prefix, dir=directory))
    temporary.rmdir()
    return temporary


def _new_staging_directory(directory: Path, prefix: str) -> Path:
    """Create a unique staging directory with a static-serving mode."""
    for _ in range(100):
        candidate = directory / f"{prefix}{uuid.uuid4().hex}"
        try:
            candidate.mkdir(mode=_REQUESTED_DIRECTORY_MODE)
        except FileExistsError:
            continue
        ensure_publishable_directory(candidate)
        return candidate
    raise OutputError(f"could not reserve staging directory below {directory}")


def _lock_path(lock_root: Path) -> Path:
    """Return the persistent lock path for one logical output root."""
    return lock_root.parent / f".{lock_root.name}.publish.lock"


def _held_lock_paths() -> set[Path]:
    """Return lock paths held by this thread for reentrant nested writes."""
    held = getattr(_LOCK_STATE, "paths", None)
    if held is None:
        held = set()
        _LOCK_STATE.paths = held
    return held


def _rollback_artifacts(destination: Path) -> list[Path]:
    """List sibling rollback artifacts using literal names, not a glob."""
    prefix = f".{destination.name}.backup-"
    try:
        entries = destination.parent.iterdir()
    except FileNotFoundError:
        return []
    return sorted(
        (entry for entry in entries if entry.name.startswith(prefix)),
        key=lambda entry: entry.name,
    )


def _recover_rollback_artifact(destination: Path) -> None:
    """Recover a destination left absent by an interrupted directory swap."""
    artifacts = _rollback_artifacts(destination)
    if not artifacts:
        return
    if _lexists(destination):
        raise OutputError(
            f"rollback artifact(s) require inspection before publishing {destination}: "
            f"{', '.join(str(path) for path in artifacts)}"
        )
    if len(artifacts) != 1:
        raise OutputError(
            f"ambiguous rollback artifacts for {destination}: "
            f"{', '.join(str(path) for path in artifacts)}"
        )
    artifact = artifacts[0]
    if artifact.is_symlink() or not artifact.is_dir():
        raise OutputError(f"invalid rollback artifact for {destination}: {artifact}")
    validate_existing_tree(artifact)
    try:
        os.replace(artifact, destination)
    except OSError as exc:
        raise OutputError(
            f"could not recover rollback artifact for {destination}: {artifact}"
        ) from exc


def _staging_artifacts(lock_root: Path) -> list[Path]:
    """List sibling staging artifacts for a logical output root literally."""
    prefix = f".{lock_root.name}.staging-"
    try:
        entries = lock_root.parent.iterdir()
    except FileNotFoundError:
        return []
    return sorted(
        (entry for entry in entries if entry.name.startswith(prefix)),
        key=lambda entry: entry.name,
    )


def _clean_orphan_staging_artifacts(lock_root: Path) -> None:
    """Remove safe-to-delete staging artifacts while its cooperative lock is held."""
    for artifact in _staging_artifacts(lock_root):
        if artifact.is_symlink() or not artifact.is_dir():
            raise OutputError(f"invalid orphan staging artifact: {artifact}")
        try:
            ensure_publishable_tree(artifact)
        except OSError as exc:
            raise OutputError(f"could not inspect orphan staging artifact: {artifact}") from exc
        try:
            _remove_tree(artifact)
        except OSError as exc:
            raise OutputError(f"could not remove orphan staging artifact: {artifact}") from exc


def _remove_nested_lock_artifacts(root: Path) -> None:
    """Drop only exact legacy lock artifacts at the copied output root."""
    for name in _KNOWN_NESTED_LOCK_ARTIFACT_NAMES:
        path = root / name
        if not _lexists(path):
            continue
        if path.is_symlink() or not path.is_file():
            raise OutputError(f"invalid nested publication lock: {path}")
        try:
            path.unlink()
        except OSError as exc:
            raise OutputError(f"could not remove nested publication lock: {path}") from exc


def _prepare_copy_directories(source: Path, target: Path) -> None:
    """Pre-create copied directories before copytree encounters restrictive umask."""
    for path in sorted(source.rglob("*"), key=lambda item: str(item)):
        if not path.is_dir():
            continue
        relative = path.relative_to(source)
        destination = target / relative
        destination.mkdir(mode=_REQUESTED_DIRECTORY_MODE, exist_ok=True)
        ensure_publishable_directory(destination)


def _remove_tree(path: Path) -> None:
    """Remove a generated directory if it still exists."""
    if _lexists(path):
        if path.is_symlink():
            path.unlink()
        else:
            shutil.rmtree(path)


@contextmanager
def _destination_lock(lock_root: Path) -> Iterator[bool]:
    """Serialize cooperating publishers for one logical output root.

    The lock file is intentionally persistent: removing it after every run
    would reintroduce a create/unlink race between cooperating writers. Linux's
    ``O_NOFOLLOW`` rejects a pre-existing lock symlink; the explicit checks also
    keep the failure clear on platforms without that flag. The lock is
    advisory, so it does not protect against an unrelated process that ignores
    it or mutates the path after validation. Nested writes in the same thread
    reuse the outer lock and therefore never place a lock file in a staging
    tree. The yielded boolean is true only for the writer that acquired it.
    """
    lock_path = _lock_path(lock_root)
    key = lock_path.resolve()
    held = _held_lock_paths()
    if key in held:
        yield False
        return
    if _lexists(lock_path) and lock_path.is_symlink():
        raise OutputError(f"refusing symlinked publication lock: {lock_path}")
    if _lexists(lock_path):
        try:
            existing_stat = os.stat(lock_path, follow_symlinks=False)
            if not stat.S_ISREG(existing_stat.st_mode):
                raise OutputError(f"publication lock is not a regular file: {lock_path}")
            os.chmod(lock_path, 0o600, follow_symlinks=False)
        except OSError as exc:
            raise OutputError(f"could not repair publication lock: {lock_path}") from exc
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise OutputError(f"could not open publication lock: {lock_path}") from exc
    try:
        try:
            lock_stat = os.fstat(fd)
            path_stat = os.stat(lock_path, follow_symlinks=False)
            if not stat.S_ISREG(lock_stat.st_mode) or not os.path.samestat(
                lock_stat, path_stat
            ):
                raise OutputError(f"publication lock is not a regular file: {lock_path}")
            os.fchmod(fd, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
        except OSError as exc:
            raise OutputError(f"could not acquire publication lock: {lock_path}") from exc
        held.add(key)
        try:
            yield True
        finally:
            held.remove(key)
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _publish(staging: Path, destination: Path) -> None:
    """Swap a completed staging directory into place with best-effort rollback."""
    backup: Path | None = None
    if _lexists(destination):
        # This is the first half of the only portable two-rename handoff for
        # replacing a non-empty directory. Keep the backup until the new tree
        # is installed and cleanup succeeds; either failure leaves an explicit
        # artifact/state for inspection rather than an unconditional guarantee.
        try:
            backup = _new_sibling(destination.parent, f".{destination.name}.backup-")
            os.replace(destination, backup)
        except OSError as exc:
            raise OutputError(
                f"could not move existing destination to a rollback artifact: {destination} "
                f"({exc})"
            ) from exc
    try:
        os.replace(staging, destination)
    except BaseException as install_error:
        if backup is not None:
            try:
                os.replace(backup, destination)
            except OSError as restore_error:
                raise OutputError(
                    f"publication failed installing {destination}; rollback also failed; "
                    f"destination may be absent and backup remains at {backup} "
                    f"({install_error}; {restore_error})"
                ) from restore_error
            if isinstance(install_error, OSError):
                raise OutputError(
                    f"publication failed installing {destination}; previous destination "
                    f"was restored ({install_error})"
                ) from install_error
        if isinstance(install_error, OSError):
            raise OutputError(
                f"publication failed installing {destination}; destination remains absent "
                f"({install_error})"
            ) from install_error
        raise
    else:
        if backup is not None:
            try:
                _remove_tree(backup)
            except Exception as exc:
                raise OutputError(
                    f"new publication installed at {destination}, but backup "
                    f"cleanup failed; inspect {backup} ({exc})"
                ) from exc


@contextmanager
def staged_directory(
    destination: Path,
    forbidden_paths: Iterable[Path] = (),
    *,
    lock_root: Path | None = None,
    cleanup_roots: Iterable[Path] = (),
) -> Iterator[Path]:
    """Yield a sibling staging directory and publish it on clean exit.

    The destination is untouched while the caller renders. An exception from
    that rendering phase removes the staging tree and leaves an existing
    destination unchanged. During publication, a failed install gets one
    rollback attempt: a successful rollback restores the old destination, but
    a failed rollback may leave the destination absent with its backup artifact
    in place. If backup cleanup fails after installation, the new destination
    remains and the backup artifact remains. These exceptional states are
    surfaced rather than reported as a successful or universally atomic
    publication. Symlink destinations and path components are rejected,
    including broken links; existing output and staging trees are checked at
    their publication boundaries, and :func:`copy_existing_tree` checks the
    copied tree as well. A per-output-root advisory lock serializes cooperating
    writers; it is not protection against an adversarial process changing paths
    concurrently. The optional ``lock_root`` lets a nested surface (for
    example ``out/data`` during a full build) share the output-root lock rather
    than creating a lock file inside the staging tree. The lock owner removes
    orphan staging directories for that root before starting; this is safe only
    for the documented cooperative single-writer model. ``cleanup_roots``
    names the root and any known nested surfaces whose orphan staging siblings
    should be cleaned by the lock owner. Creation requests ``0755``/``0644``
    modes through the process umask; the final tree deliberately repairs those
    public static-serving modes, with executable bits only on directories.
    """
    destination = Path(destination)
    logical_root = destination if lock_root is None else Path(lock_root)
    orphan_roots = tuple(Path(root) for root in cleanup_roots) or (logical_root,)
    validate_destination(destination, forbidden_paths)
    validate_destination(logical_root, forbidden_paths)
    for root in orphan_roots:
        validate_destination(root, forbidden_paths)
    try:
        _prepare_output_parent(logical_root.parent)
    except OSError as exc:
        raise OutputError(f"cannot create output lock parent: {logical_root.parent}") from exc
    with _destination_lock(logical_root) as lock_owner:
        if lock_owner:
            for root in orphan_roots:
                _clean_orphan_staging_artifacts(root)
        try:
            _prepare_output_parent(destination.parent)
        except OSError as exc:
            raise OutputError(f"cannot create output parent: {destination.parent}") from exc
        # Parent creation can itself expose a newly-created path component.
        # Recheck while the cooperative single-writer lock is held; this is not
        # advertised as a race-free defense against an independent path-mutating
        # process.
        validate_destination(destination, forbidden_paths)
        validate_destination(logical_root, forbidden_paths)
        for root in orphan_roots:
            validate_destination(root, forbidden_paths)
        validate_existing_tree(destination)
        _recover_rollback_artifact(destination)
        try:
            staging = _new_staging_directory(
                destination.parent, f".{destination.name}.staging-"
            )
        except OSError as exc:
            raise OutputError(
                f"could not create staging directory for {destination}"
            ) from exc
        try:
            yield staging
            try:
                ensure_publishable_tree(staging)
            except OSError as exc:
                raise OutputError(
                    f"could not prepare staging directory for {destination}"
                ) from exc
            _publish(staging, destination)
        except BaseException as operation_error:
            try:
                _remove_tree(staging)
            except OSError as cleanup_error:
                raise OutputError(
                    f"publication operation for {destination} failed and staging "
                    f"cleanup also failed: {staging} ({operation_error}; {cleanup_error})"
                ) from cleanup_error
            raise


def copy_existing_tree(destination: Path, staging: Path) -> None:
    """Copy a prior build into staging before applying a partial surface.

    ``vitrine export`` updates the data surface without deleting an already
    built museum.  Existing output is generated locally, so preserving its
    directory structure is safe. ``copytree(..., symlinks=True)`` copies link
    objects rather than dereferencing them; the completed staging tree is then
    checked and rejected if any link was present. The preflight and post-copy
    checks are still subject to the documented non-adversarial single-writer
    threat model.
    """
    validate_destination(destination)
    validate_existing_tree(destination)
    if not destination.is_dir():
        return
    try:
        _prepare_copy_directories(destination, staging)
        shutil.copytree(destination, staging, dirs_exist_ok=True, symlinks=True)
    except OSError as exc:
        raise OutputError(f"could not preserve existing output: {destination}") from exc
    ensure_publishable_tree(staging)
    _remove_nested_lock_artifacts(staging)
    ensure_publishable_tree(staging)


__all__ = [
    "OutputError",
    "copy_existing_tree",
    "ensure_publishable_directory",
    "ensure_publishable_file",
    "ensure_publishable_tree",
    "staged_directory",
    "validate_destination",
    "validate_existing_tree",
]
