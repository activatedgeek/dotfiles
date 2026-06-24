from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@dataclass
class Jq(Binary):
    gh_repo: ClassVar[str] = "jqlang/jq"
    version: ClassVar[str] = "jq-1.8.2"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "jq-linux64",
                "sha256sum": "b1c22172dd303f3be49e935aa56aa48a8b7a46e0bc838b4997d3bb451495870f",
            },
            "arm64": {
                "name": "jq-linux-arm64",
                "sha256sum": "8b85c817833814ddca00a144c33705546355afccf0cf39b188f3cdb48b852309",
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
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall",
            path=f"{remote_home}/.local/bin/jq",
            present=False,
        )
    else:
        binary = Jq(arch)

        files.download(
            name="Install",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/jq",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("Jq")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
