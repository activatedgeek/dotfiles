---
name: update-binaries
description: Update selected precompiled binaries in pyinfra/tasks by comparing release versions, recalculating checksums for installed executables, and patching their apply.py definitions. Use when asked to update binaries, package versions, or checksums in this repository.
---

# Update Binaries

Update one or more binaries defined under `pyinfra/tasks/`. The checksum stored
in each `Binary.asset_map` is the SHA-256 of the executable that ends up at the
task's destination, not the downloaded archive.

Always use `uv` to run Python commands in this repository. Use `uv run
python ...` for imports, scripts, and validation; do not invoke `python` or
`python3` directly.

## Inputs

Use the binary names supplied by the user. Accept task directory names, class
names, and executable names case-insensitively. Examples include `uv`, `uvx`,
`opencode`, and `mise`.

If the user does not provide a list, ask for one rather than updating every
binary implicitly. Resolve each requested name to the corresponding
`pyinfra/tasks/<task>/apply.py` class that subclasses
`pkgs/myinfra/src/myinfra/utils/binary.py:Binary`.

## Discovery

1. Read `pkgs/myinfra/src/myinfra/utils/binary.py` to understand `Binary.src`,
   `Binary.sha256sum`, and architecture names (`amd64` and `arm64`).
2. Locate the requested class definitions under `pyinfra/tasks/**/apply.py`.
   Record the class name, `version`, `gh_repo`, both `asset_map` entries, and
   the operation that installs the binary.
3. Inspect the task's `myfiles.download` or `files.download` call to determine
   the final executable path and whether `src_dir` is used. This identifies the
   exact file inside an archive to hash. Do not assume the archive checksum is
   valid for the installed executable.
4. Import and call `get_latest_binary_versions(tasks_dir, cache_dir, cache_ttl)`
   from `myinfra.utils.config` to obtain the latest-version dictionary. Use the
   same cache settings as `pyinfra/config.py`: `PYINFRA_CACHE_HOME`, defaulting
   to `pyinfra/.pyinfra_cache`, and `PYINFRA_CACHE_TTL`, defaulting to 24 hours.
   For example, from the repository root:

   ```python
   import os
   from pathlib import Path

   from myinfra.utils.config import get_latest_binary_versions

   cache_dir = Path(os.getenv("PYINFRA_CACHE_HOME", Path("pyinfra") / ".pyinfra_cache"))
   cache_ttl = int(os.getenv("PYINFRA_CACHE_TTL", 24 * 60 * 60))
   versions = get_latest_binary_versions(Path("pyinfra") / "tasks", cache_dir=cache_dir, cache_ttl=cache_ttl)
   ```

   Run this with `uv run python ...`. Compare the
   requested classes' current `version` values with the corresponding
   dictionary entries. Do not replace the configured cache with a temporary
   cache merely to force a refresh; the helper's configured cache is the source
   of truth for the project's normal pyinfra environment.

If every selected class already has the version returned by the helper, report
that no version bumps are needed and stop immediately. Do not download assets,
recalculate checksums, patch task files, or run post-edit validation in that
case. Only continue with the checksum, editing, and validation workflows when
at least one selected class has a version bump.

Do not use a release's latest version blindly when the helper returns a value.
Use the exact version returned for the selected class. If the helper cannot be
run, report the missing prerequisite instead of guessing a version.

## Checksum Workflow

For each selected binary and each architecture:

1. Build the release asset URL from `gh_repo`, the new version, and the asset
   name from `asset_map`.
2. Create one temporary directory for the operation and register cleanup before
   downloading anything. Use a shell trap covering normal exit and interrupts,
   for example:

   ```bash
   tmp_dir="$(mktemp -d)"
   cleanup() { rm -rf "$tmp_dir"; }
   trap cleanup EXIT HUP INT TERM
   ```

3. Download the asset into that directory. Never leave downloaded archives,
   extracted files, or checksum intermediates in the repository or temporary
   directory after the operation.
4. If the asset is an archive (`.tar.gz`, `.tar.bz2`, `.tar.zst`, or `.zip`),
   inspect its contents and extract it into the temporary directory. Hash the
   exact executable installed by the task, such as `uv`, `uvx`, `btm`, or
   `opencode`, using `shasum -a 256` or an equivalent tool. If an archive
   contains multiple executables, hash only the one corresponding to the task's
   destination.
5. If the asset is a raw executable, hash the downloaded file itself. This is
   the case for task definitions such as `mise` that use `files.download`
   without an archive.
6. Verify that both architecture values produce a 64-character lowercase
   SHA-256 value. Keep separate checksums for separate binaries even when they
   share one archive, as `uv` and `uvx` do.

Use quoted paths and fail-fast commands. Prefer release-provided metadata only
as a cross-check; a digest reported for a `.tar.gz` or `.zip` is not the value
to place in `sha256sum`.

## Editing

Patch only the selected `apply.py` files:

- Update the class `version` to the value returned by
  `get_latest_binary_versions(tasks_dir, cache_dir, cache_ttl)` using the
  cache configuration above.
- Keep `gh_repo` and asset names unchanged unless the release has demonstrably
  changed them and the task must follow that change.
- Replace each selected `amd64` and `arm64` `sha256sum` with the hash of the
  installed executable.
- Update every selected `Binary` class separately when multiple classes use the
  same asset.
- Preserve unrelated user changes. Do not reformat or rewrite whole files.

Do not commit changes unless the user explicitly asks for a commit.

## Validation

After editing:

1. Confirm each requested class has the intended version and two updated
   architecture checksums.
2. Run `git diff --check`.
3. Run Python syntax validation for the changed files, for example:
   `uv run python -m compileall -q <changed apply.py files>`.
4. Inspect `git diff` and confirm only the requested task definitions changed.
   Ignore unrelated pre-existing worktree changes and never revert them.
5. Confirm the temporary directory is gone and no downloaded archive or
   extraction artifact remains. If cleanup failed, remove only the temporary
   paths created by this operation before reporting completion.

Report the updated binaries, versions, architectures, and validation results.
