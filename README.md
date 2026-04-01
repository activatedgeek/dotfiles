# dotfiles

[![Prek](https://github.com/activatedgeek/dotfiles/actions/workflows/prek.yml/badge.svg)](https://github.com/activatedgeek/dotfiles/actions/workflows/prek.yml)

## Setup

Install [`homebrew`](https://brew.sh),
```shell
/usr/bin/env bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

and install [`uv`](https://docs.astral.sh/uv/) for Python environments,
```shell
brew install mise gpg2
```

Install using,
```shell
mise setup
```

### Environment Variables

Setup the following environment variables (optionally in a `pyinfra/.env` file).
- `BWS_ACCESS_TOKEN`: Bitwarden Secrets token. See [docs](https://bitwarden.com/help/secrets-manager-cli/#authentication).

```shell
BWS_ACCESS_TOKEN="<token>"
```

### SSH

Generate SSH keys and copy then to target host,
```shell
mise keygen home --auth-host <user>@<host>
```

Then run,
```shell
mise deploy home
```

## Deploy

Finally, run,
```shell
mise deploy home
```

Use `--teardown` flag to remove all changes.

**TIP**: See `mise deploy -h` for all CLI arguments.
