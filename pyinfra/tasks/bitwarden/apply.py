from myinfra.facts import brew as brew_facts
from myinfra.operations import launchd as mylaunchd
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall CLI",
        packages=["bitwarden-cli"],
        present=not teardown,
    )


@deploy("Backup")
def apply_backup(teardown=False):
    remote_home = host.get_fact(server_facts.Home)
    brew_prefix = host.get_fact(brew_facts.BrewPrefix)

    backup_dir = host.data.backup_dir.replace("~/", f"{remote_home}/", 1).replace("\\ ", " ")

    if not teardown:
        files.line(
            name="Password",
            path=f"{remote_home}/.config/bw/pass",
            line=host.data.vault_pass,
        )
        files.file(name="Password Permissions", path=f"{remote_home}/.config/bw/pass", mode=600)

    mylaunchd.plist(
        name=f"{'Remove ' if teardown else ''}LaunchAgent",
        src="tasks/bitwarden/templates/com.sanyamkapoor.bitwarden.plist.j2",
        service="com.sanyamkapoor.bitwarden",
        stdout_path=f"{remote_home}/Library/Logs/Bitwarden/launchtl-export.log",
        bw_path=f"{brew_prefix}/bin/bw",
        password_path=f"{remote_home}/.config/bw/pass",
        backup_path=f"{backup_dir}/Credentials/bw-vault.zip",
        present=not teardown,
    )

    if teardown:
        files.file(name="Remove Password", path=f"{remote_home}/.config/bw/pass", present=False)


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if not teardown:
        files.directory(name="Directory", path=f"{remote_home}/.config/bw", mode=700)

    if "home" in host.groups:
        apply_backup(teardown=teardown)

    if teardown:
        files.directory(name="Remove Directory", path=f"{remote_home}/.config/bw", present=False)


@deploy("Bitwarden")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
        apply_config(teardown=teardown)
