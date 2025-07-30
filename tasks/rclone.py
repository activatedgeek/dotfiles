from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.operations import files, brew
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://downloads.rclone.org/
class Rclone:
    version = "1.70.2"

    class Linux:
        sha256sum = "d1d99f58c1ad31592caa093eb400607725afd74eb3655bdeb6dc1886fed8fda8"


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
    linux_hosts = {
        host.name: {
            "hostname": host.data.ssh_hostname,
            "store_home": host.data.store_home.replace("${USER}", host.data.ssh_user),
        }
        for host in inventory.get_group("linux")
    }

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Conf",
        src="templates/rclone/nvda-rclone.conf.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.config/rclone/rclone.conf",
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

    if host.data.get("org", "") == "nvda" and "linux" in host.groups:
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
