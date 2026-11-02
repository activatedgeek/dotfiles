from shlex import quote

from myinfra.operations import launchd as mylaunchd
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@deploy("Backup")
def apply_backup(teardown=False):
    remote_home = host.get_fact(server_facts.Home)
    source_dir = host.data.get("obsidian_dir", "~/Obsidian").replace("~/", f"{remote_home}/", 1)
    backup_dir = host.data.backup_dir.replace("~/", f"{remote_home}/", 1).replace("\\ ", " ")

    if not teardown:
        files.directory(name="Backup Directory", path=backup_dir, mode=700)

    mylaunchd.plist(
        name=f"{'Remove ' if teardown else ''}LaunchAgent",
        service="com.sanyamkapoor.obsidian",
        src="tasks/obsidian/templates/com.sanyamkapoor.obsidian.plist.j2",
        stdout_path=f"{remote_home}/Library/Logs/Obsidian/launchctl-backup.log",
        source_dir=quote(source_dir),
        backup_path=quote(f"{backup_dir}/Obsidian.tar.gz"),
        present=not teardown,
    )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["obsidian"],
        present=not teardown,
    )


@deploy("Obsidian")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
        if "home" in host.groups:
            apply_backup(teardown=teardown)
