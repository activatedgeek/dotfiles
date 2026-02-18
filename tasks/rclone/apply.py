from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://downloads.rclone.org/
@dataclass
class Rclone(Binary):
    version: ClassVar[str] = "1.73.1"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://downloads.rclone.org/v{self.version}/rclone-v{self.version}-linux-amd64.zip",
                "sha256sum": "10ffca7640f0483beba9a9c9f4cdb6a9ca30a13c4ab31f2329d09a832802694d",
            },
            "arm64": {
                "src": f"https://downloads.rclone.org/v{self.version}/rclone-v{self.version}-linux-arm64.zip",
                "sha256sum": "ea441b0133a824920af5d061b4fb66a49799fc450d6e3658f8f21e22fbe2aec0",
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
    remote_home = host.get_fact(server_facts.Home)

    linux_hosts = {
        f"{ihost.name.split('/')[-1]}": {
            "hostname": ihost.data.ssh_hostname,
            "port": ihost.data.get("ssh_port", 22),
        }
        for ihost in inventory.get_group("linux")
    }

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Conf",
        src="tasks/rclone/templates/nvda-rclone.conf.j2",
        dest=f"{remote_home}/.config/rclone/rclone.conf",
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
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)


apply()
