from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.operations import files as myfiles


## https://downloads.rclone.org/
class Rclone:
    version = "1.71.1"

    class Linux:
        sha256sum = "5409cb410e49903af3517654ccc65c89d89f9dc12d7a97b0e13e09a9be6dc74a"


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["rclone"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=f"https://downloads.rclone.org/v{Rclone.version}/rclone-v{Rclone.version}-linux-amd64.zip",
        src_dir=f"rclone-v{Rclone.version}-linux-amd64",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/rclone",
        sha256sum=Rclone.Linux.sha256sum,
        present=not teardown,
        mode=755,
    )


@deploy("NVDA")
def apply_nvda(teardown=False):
    homedir = host.get_fact(server_facts.Home)

    linux_hosts = {
        f"{ihost.name.split('/')[-1]}": {
            "hostname": ihost.data.ssh_hostname,
            "store_home": ihost.data.store_home.replace("${USER}", host.data.ssh_user).replace("${HOME}", homedir),
        }
        for ihost in inventory.get_group("linux")
    }

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Conf",
        src="templates/rclone/nvda-rclone.conf.j2",
        dest=f"{homedir}/.config/rclone/rclone.conf",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        hosts=linux_hosts,
    )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{host.get_fact(server_facts.Home)}/.config/rclone",
        present=not teardown,
        mode=700,
    )

    if host.data.get("org", "") == "nvda":
        apply_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        apply_linux(teardown=teardown)

    apply_config(teardown=teardown)


apply()
