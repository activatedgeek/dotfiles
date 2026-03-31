from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host, inventory


@dataclass
class Rclone(Binary):
    gh_repo: ClassVar[str] = "rclone/rclone"
    version: ClassVar[str] = "v1.73.3"

    @property
    def asset_map(self) -> dict[str, dict[str, str]]:
        return {
            "amd64": {
                "name": f"rclone-{self.version}-linux-amd64.zip",
                "sha256sum": "41bd63149d3bd281f9d8fb02fd8c0406234634a59cd0f591b86ad3f1e2f6abb7",
            },
            "arm64": {
                "name": f"rclone-{self.version}-linux-arm64.zip",
                "sha256sum": "d0e0c8eb62ca0bbd74f3e61e274a3c27103ca2c31e59e6b468018c87d364c0d9",
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
        src_dir=f"rclone-{binary.version}-linux-{Path(binary.src).stem.split('-')[-1]}",
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
        if not ihost.data.get("skip_host", False)
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
        dagshub_username=host.data.get("dagshub_username"),
        dagshub_user_token=host.data.get("dagshub_user_token"),
    )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{host.get_fact(server_facts.Home)}/.config/rclone",
        present=not teardown,
        mode=700,
    )

    if "nvda" in host.groups:
        apply_nvda(teardown=teardown)


@deploy("Rclone")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)
