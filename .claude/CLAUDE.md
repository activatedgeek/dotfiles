# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies and pre-commit hooks
mise setup

# Deploy to an inventory (See pyinfra/inventories for a list)
mise deploy <inventory>

# Deploy only a specific task
mise deploy <inventory> --task <task_name>

# Limit to specific hosts
mise deploy <inventory> --limit <host>

# Refresh secrets/version cache before deploying
mise deploy <inventory> --refresh

# Teardown a deployment
mise deploy <inventory> --teardown
```

## Architecture

This repo uses **pyinfra** for declarative, idempotent machine configuration, with **mise** as the task runner and **Bitwarden Secrets Manager** for secrets.

### Deployment Flow

`mise deploy <inventory>` → `pyinfra/deploy.py`:
1. Loads host data from `pyinfra/inventories/<inventory>.py`
2. Collects all task names from `pyinfra/tasks/*/`
3. Filters by `host.data["skip_tasks"]` and optional `apply_tasks`
4. Dynamically imports and calls `apply()` from each `tasks/<name>/apply.py`

### Task Structure

Each task lives in `pyinfra/tasks/<name>/apply.py` and follows this pattern:

```python
@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(packages=[...], present=not teardown)

@deploy("Main")
def apply(teardown=False):
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    apply_config(teardown=teardown)
```

Tasks receive `teardown=host.data.get("teardown", False)` and are expected to be idempotent.

### Inventories

- `home.py` — personal Mac (`@local`) + cloud infrastructure; skips enterprise tools (`enroot`, `nemo`)
- `nvda.py` — NVIDIA infrastructure: desktop hosts (`desk`, `bigdesk`) and SLURM clusters (`dfw`, `eos`, `hsg`, `iad`, `lax`, `nrt`, `ord`); skips personal tools (`bitwarden`, `brave`, `slack`, etc.)

Hosts can set `skip_host=True` to be excluded from deploys by default.

### Custom Packages

**`packages/myinfra/`** — extends pyinfra:
- `facts/` — custom system introspection (Homebrew prefix, Debian arch, SLURM, SSH state, etc.)
- `operations/` — `files.template()`, `files.download()` (with SHA256 verify), `archive.tar/unzip`, and tool-specific ops
- `utils/Binary` — base class for managing pre-compiled binaries: GitHub release fetching, arch-specific asset maps, SHA256 validation

**`packages/xfiles/`** — ML experiment file utilities (Aim/MLflow optional).

### Secret & Cache Management (`pyinfra/config.py`)

Secrets are fetched from Bitwarden SDK using `BWS_ACCESS_TOKEN` in `pyinfra/.env`, and cached in `.pyinfra_cache/` for 1 day. Binary latest-version checks (GitHub API) are also cached here. Pass `--refresh` to wipe the cache.

### Binary Version Management

Tasks define `Binary` subclasses with `gh_repo`, `version`, and `asset_map` (arch → filename + sha256sum). At deploy time, `config.py` checks GitHub for newer releases and logs warnings if the hardcoded version is outdated.
