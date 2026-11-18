from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@dataclass
class Yq(Binary):
    gh_repo: ClassVar[str] = "mikefarah/yq"
    version: ClassVar[str] = "v4.54.3"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "yq_linux_amd64",
                "sha256sum": "129534601871538efe0ba4c5e62a34fb1d5f469bcb975c4fddeb467d82974973",
            },
            "arm64": {
                "name": "yq_linux_arm64",
                "sha256sum": "89f69310b61b68d1245065a1241d1fc843f7a36cd6103ffd77ad987613bd1b67",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["yq"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall",
            path=f"{remote_home}/.local/bin/yq",
            present=False,
        )
    else:
        binary = Yq(arch)

        files.download(
            name="Install",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/yq",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("Yq")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
