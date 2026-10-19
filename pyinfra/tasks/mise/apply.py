from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@dataclass
class Mise(Binary):
    gh_repo: ClassVar[str] = "jdx/mise"
    version: ClassVar[str] = "v2026.10.15"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": f"mise-{self.version}-linux-x64",
                "sha256sum": "e3b186d4c70627f27037be615becaf4acfb30e41fb6a1819486717dc94e4e2a9",
            },
            "arm64": {
                "name": f"mise-{self.version}-linux-arm64",
                "sha256sum": "3abbaac305a465ef038eb4ea07b961c037a8b639108005e43f8e2c00a8f67c11",
            },
        }


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall mise",
            path=f"{remote_home}/.local/bin/mise",
            present=False,
        )
    else:
        binary = Mise(arch)

        files.download(
            name="mise",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/mise",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["mise"],
        present=not teardown,
    )


@deploy("Mise")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
