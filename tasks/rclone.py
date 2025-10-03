from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://downloads.rclone.org/
@dataclass
class Rclone(Binary):
    version: ClassVar[str] = "1.71.1"

    @property
    def _arch_map(self):
        return {
            "x86_64": {
                "src": f"https://downloads.rclone.org/v{self.version}/rclone-v{self.version}-linux-amd64.zip",
                "sha256sum": "5409cb410e49903af3517654ccc65c89d89f9dc12d7a97b0e13e09a9be6dc74a",
            },
            "aarch64": {
                "src": f"https://downloads.rclone.org/v{self.version}/rclone-v{self.version}-linux-arm64.zip",
                "sha256sum": "024871b9bc0c47311e73ed06b1abf13208723b79b51d55b5a757d787e9340c13",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["rclone"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    binary = Rclone(arch)
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        src_dir=f"rclone-v{binary.version}-linux-{Path(binary.src).stem.split('-')[-1]}",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/rclone",
        sha256sum=binary.sha256sum,
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
        arch = host.get_fact(server_facts.Arch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)


apply()
