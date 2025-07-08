# dotfiles

[![Lint](https://github.com/activatedgeek/dotfiles/actions/workflows/lint.yml/badge.svg)](https://github.com/activatedgeek/dotfiles/actions/workflows/lint.yml)

## Setup

Install [`homebrew`](https://brew.sh),
```shell
/usr/bin/env bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

and install [`uv`](https://docs.astral.sh/uv/) for Python environments,
```shell
brew install uv
```

Create a virtual environment with `uv venv`, and install,
```shell
make install
```

### Environment Variables

Setup the following environment variables (optionally in a `.env` file).
- `BWS_ORG_ID`: Bitwarden Organization ID to get secrets from. See [docs](https://bitwarden.com/help/secrets-manager-cli/#authentication).
- `BWS_ACCESS_TOKEN`: Bitwarden Secrets token to get secrets. See [docs](https://github.com/bitwarden/sdk/tree/main/languages/python).

```shell
BWS_ORG_ID="<id>"
BWS_ACCESS_TOKEN="<token>"
```

### SSH

Generate SSH keys using,
```shell
ssh-keygen -t ed25519 -f "$(pwd)/id_ed25519" -C "$(whoami)"
```
and move to appropriate folder under [SSH files](./files/ssh).
See SSH [`task`](./tasks/ssh.py) for accessed paths.

Then run,
```shell
make infra.home
```

Authorize each target remote host manually from the [`inventory`](./inventory) to use the SSH key,
```shell
ssh-copy-id -i files/ssh/<org>/id_ed25519 <host>
```

## Deploy

Finally, run,
```shell
make infra.home
```

### Dedeploy

For teardown tasks,
```shell
make uninfra.home
```
