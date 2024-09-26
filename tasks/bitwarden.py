from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew, server
from pyinfra.facts import server as server_facts

from myinfra.facts import brew as brew_facts


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall CLI",
        packages=["bitwarden-cli"],
        present=not teardown,
    )


@deploy("Backup")
def apply_backup(teardown=False):
    ## Backup every hour.
    server.crontab(
        name="Vault",
        command=f"echo '{host.data.vault_pass}' | {host.get_fact(brew_facts.BrewPrefix)}/bin/bw export --format encrypted_json --password '{host.data.vault_pass}' --output {host.data.backup_dir}/vault.json >>/tmp/vault-export.bw.log 2>&1",
        minute="0",
        hour="*",
        month="*",
        day_of_week="*",
        day_of_month="*",
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
        apply_backup(teardown=teardown)


apply()
