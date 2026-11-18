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
    version: ClassVar[str] = "v2026.11.9"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": f"mise-{self.version}-linux-x64",
                "sha256sum": "f13f3e5ec88807e0161669b3aa07a91d84478cdf1e95b5b92b63f85a25d42395",
            },
            "arm64": {
                "name": f"mise-{self.version}-linux-arm64",
                "sha256sum": "b8dd05af6447cee933928664982a8cb2fa646e6951cfc8539db23ce2554a7b04",
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
