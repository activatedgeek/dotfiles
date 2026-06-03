from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from pyinfra import host


@dataclass
class Zellij(Binary):
    gh_repo: ClassVar[str] = "zellij-org/zellij"
    version: ClassVar[str] = "v0.44.3"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "zellij-no-web-x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "a675b0106263113b9cb8f028649bad05c5d2283331fa62b2b36dd275aeaaa4d3",
            },
            "arm64": {
                "name": "zellij-no-web-aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "6c06fd6139c2e38c6a07e0471b0662d08123ce35b436800d0c7017125f8ce4af",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["zellij"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    binary = Zellij(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/zellij",
        sha256sum=binary.sha256sum,
        present=not teardown,
        mode=755,
    )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Settings",
        src="tasks/zellij/files/config.kdl",
        dest=f"{remote_home}/.config/zellij/config.kdl",
        mode=600,
        present=not teardown,
    )


@deploy("Zellij")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)
