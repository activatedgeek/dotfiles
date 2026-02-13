from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary


## https://github.com/jdx/mise/releases
@dataclass
class Mise(Binary):
    version: ClassVar[str] = "v2026.2.11"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/jdx/mise/releases/download/{self.version}/mise-{self.version}-linux-x64",
                "sha256sum": "3e1baedb9284124b770d2d561a04a98c343d05967c83deb8b35c7c941f8d9c9a",
            },
            "arm64": {
                "src": f"https://github.com/jdx/mise/releases/download/{self.version}/mise-{self.version}-linux-arm64",
                "sha256sum": "14334e8088e6a89148d2ec153fccc720be0391c6e2719ad6d94e33f91ab6e3a6",
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


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)


apply()
