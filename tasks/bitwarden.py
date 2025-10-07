from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files, server

from myinfra.facts import brew as brew_facts


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall CLI",
        packages=["bitwarden-cli"],
        present=not teardown,
    )


@deploy("Home")
def apply_config_home(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name="Directory",
        path=f"{remote_home}/.config/bw",
        present=not teardown,
    )

    if host.data.get("vault_pass", None):
        files.line(
            name="Vault Password",
            path=f"{remote_home}/.config/bw/pass",
            line=host.data.vault_pass,
            present=not teardown,
        )

        files.file(
            name="Permissions",
            path=f"{remote_home}/.config/bw/pass",
            mode=600,
            present=not teardown,
        )

        server.crontab(
            name="Backup Vault",
            command=f'cat ~/.config/bw/pass | {host.get_fact(brew_facts.BrewPrefix)}/bin/bw export --format encrypted_json --password "$(cat ~/.config/bw/pass)" --output {host.data.backup_dir}/vault.json >>/tmp/vault-export.bw.log 2>&1',
            minute="0",
            hour="*/18",
            month="*",
            day_of_week="*",
            day_of_month="*",
            present=not teardown,
        )


@deploy("Config")
def apply_config(teardown=False):
    if host.data.get("org", "") == "me":
        apply_config_home(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
        apply_config(teardown=teardown)


apply()
