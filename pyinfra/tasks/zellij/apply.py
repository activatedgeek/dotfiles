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
    version: ClassVar[str] = "v0.44.1"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "zellij-no-web-x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "f55f0fb825d7cde5d6194127453e07b7e99d015bc9ccc6239dd26e785f2165cc",
            },
            "arm64": {
                "name": "zellij-no-web-aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "b12771c452f8509c32a1faa242457dd3126f40acc774c2ff3d1d3a46bd2b9843",
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


@deploy("Zellij")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
