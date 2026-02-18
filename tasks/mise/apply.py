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
    version: ClassVar[str] = "v2026.2.16"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/jdx/mise/releases/download/{self.version}/mise-{self.version}-linux-x64",
                "sha256sum": "4bfb9e5cea1c5b03f63b617361b97439e6ac676c9438b6162eee24149029bbcf",
            },
            "arm64": {
                "src": f"https://github.com/jdx/mise/releases/download/{self.version}/mise-{self.version}-linux-arm64",
                "sha256sum": "391e1ccff0d04dc61927f71077c72f0555728009d8c1a5f0ee28840f3dfdbd98",
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
