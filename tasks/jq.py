from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary


## https://github.com/jqlang/jq/releases
@dataclass
class Jq(Binary):
    version: ClassVar[str] = "1.8.1"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/jqlang/jq/releases/download/jq-{self.version}/jq-linux64",
                "sha256sum": "020468de7539ce70ef1bceaf7cde2e8c4f2ca6c3afb84642aabc5c97d9fc2a0d",
            },
            "arm64": {
                "src": f"https://github.com/jqlang/jq/releases/download/jq-{self.version}/jq-linux-arm64",
                "sha256sum": "6bc62f25981328edd3cfcfe6fe51b073f2d7e7710d7ef7fcdac28d4e384fc3d4",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["jq"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    if teardown:
        files.file(
            name="Uninstall",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/jq",
            present=False,
        )
    else:
        binary = Jq(arch)
        files.download(
            name="Install",
            src=binary.src,
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/jq",
            sha256sum=binary.sha256sum,
            mode=755,
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
