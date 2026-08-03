from myinfra.facts import brew as brew_facts
from myinfra.operations import files as myfiles
from pyinfra.api import deploy
from pyinfra.facts import launchd as launchd_facts
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files, server

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

    service_label = "com.sanyamkapoor.bitwarden"
    plist_path = f"{remote_home}/Library/LaunchAgents/{service_label}.plist"
    backup_dir = host.data.backup_dir.replace("~/", f"{remote_home}/", 1).replace("\\ ", " ")

    service_loaded = service_label in host.get_fact(launchd_facts.LaunchdStatus)
    if teardown and service_loaded:
        server.shell(
            name="Bootout LaunchAgent",
            commands=f'launchctl bootout "gui/$(id -u)/{service_label}"',
        )

    files.line(
        name=f"{'Delete ' if teardown else ''}Password",
        path=f"{remote_home}/.config/bw/pass",
        line=host.data.vault_pass,
        present=not teardown,
    )
    files.file(name="Password Permissions", path=f"{remote_home}/.config/bw/pass", mode=600, present=not teardown)

    launch_agent = myfiles.template(
        name=f"{'Remove ' if teardown else ''}LaunchAgent",
        src="tasks/bitwarden/templates/com.sanyamkapoor.bitwarden.plist.j2",
        dest=plist_path,
        mode=600,
        present=not teardown,
        stdout_path=f"{remote_home}/Library/Logs/Bitwarden/launchtl-export.log",
        bw_path=f"{brew_prefix}/bin/bw",
        password_path=f"{remote_home}/.config/bw/pass",
        backup_path=f"{backup_dir}/bw-vault.zip",
    )

    if not teardown:
        server.shell(
            name="Bootstrap LaunchAgent",
            commands=[
                f'plutil -lint "{plist_path}"',
                f'launchctl bootout "gui/$(id -u)/{service_label}" >/dev/null 2>&1 || true',
                f'launchctl bootstrap "gui/$(id -u)" "{plist_path}"',
            ],
            _if=lambda: launch_agent.did_change() or not service_loaded,
        )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{remote_home}/.config/bw",
        mode=700,
        present=not teardown,
    )

    files.directory(
        name=f"{'Remove ' if teardown else ''}Log Directory",
        path=f"{remote_home}/Library/Logs/Bitwarden",
        mode=700,
        present=not teardown,
    )

    files.directory(
        name="LaunchAgents Directory",
        path=f"{remote_home}/Library/LaunchAgents",
        mode=700,
        present=not teardown,
    )

    if "home" in host.groups:
        apply_backup(teardown=teardown)


@deploy("Bitwarden")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
        apply_config(teardown=teardown)
