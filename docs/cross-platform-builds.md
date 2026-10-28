# Cross-platform builds and local publication

The CLI supports Windows and POSIX using only the standard library in the
core. Install the locked development environment with
`uv sync --locked --extra dev`, then use `uv run vitrine check`,
`uv run vitrine build`, or `uv run vitrine export` from either shell.

HTML, JSON, CSS, JavaScript and manifests are written explicitly as UTF-8
with LF line endings. CSV retains its explicitly selected writer's line
endings on both platforms. Build and render-coverage commands are tested in
subprocesses with UTF-8 mode disabled and a legacy cp1252 console codec;
successful output must remain valid UTF-8. Test fixtures use UTF-8, so run
the full suite with `uv run python -X utf8 -m pytest -q`.

## Cooperating writers and interrupted output

Both platforms use a persistent sibling lock file per logical output root.
POSIX uses `flock`; Windows locks its first byte through `msvcrt.locking`.
Windows can lock a region past EOF, so an empty lock file needs no
initialization write. The nonblocking Windows primitive retries contention
until acquisition or interruption, preserving the existing blocking contract
for builds longer than the native primitive's ten retries. Other errors
propagate. Nested writes in the same thread reuse the outer lock.

See the [Python documentation](https://docs.python.org/3/library/msvcrt.html)
and [Microsoft runtime reference](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/locking)
for the byte-region and error behavior.

Completed output is installed with the same staging/backup protocol on both
platforms. A failed render preserves the previous output. A failed install
attempts rollback; failed rollback or cleanup leaves named inspection
artifacts and an error. A subsequent cooperating writer removes safe orphan
staging directories after acquiring the lock. Real subprocess tests cover
serialization and abrupt writer exit; thread and injected-failure tests cover
reentrancy and rollback. Readers may observe the existing two-rename gap.

This remains a local, non-adversarial writer contract. It does not prevent an
unrelated process from changing paths after validation. Windows may refuse a
rename while another application has a file open; the operation reports that
failure instead of promising an installed tree.

## Permissions and path links

POSIX publication repairs generated directory/file modes to 0755/0644 and
keeps lock files at 0600. Existing private parent modes are preserved.
Windows preserves inherited ACLs and clears read-only attributes when needed;
POSIX mode bits cannot configure a Windows ACL. The publisher does not claim
to grant access beyond the parent directory's ACL.

Destination components and existing output trees reject both symbolic links
and Windows directory junctions. Native Windows tests create junctions without
requiring symlink privileges, assert rejection and verify the target's
sentinel remains intact. Actual symlink tests may require Developer Mode or
privilege on Windows; POSIX tests continue to exercise the full symlink path.

The Windows CI lane runs core validation, derivations, export/publication and
recovery tests on supported Python versions. The Linux lanes also exercise
the browser with production CSP. Source-archive replay still requires the
gitignored publisher files; a checkout without them cannot establish that
stronger evidence by running software tests alone.

## Review qualification, 28 October 2026

Native Windows Python 3.14.6 passed 238 core/publication tests. Linux Python
3.13.13 and 3.14.4 each passed the full 1,015-test source-backed suite and
67 subtests; four Windows-only tests were skipped there. All 253 generated
site files compared byte-for-byte equal across Windows and Linux, including
HTML, JavaScript, CSS, manifests and corpus exports. These are local results;
the newly authored hosted CI matrix has not run on this unpublished branch.
The broader Windows Python 3.13 run passed 826 tests and 53 subtests, with
52 skips for source archives, optional readers and platform/privilege cases.
Five browser-focused modules were excluded there; the Linux full runs include
them. The legacy-console tests explicitly disable UTF-8 mode in child processes.
