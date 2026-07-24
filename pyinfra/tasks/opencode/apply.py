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
class OpenCode(Binary):
    gh_repo: ClassVar[str] = "anomalyco/opencode"
    version: ClassVar[str] = "v1.18.4"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "opencode-linux-x64.tar.gz",
                "sha256sum": "6ce6570e7db9a40e7bd3304ebdfff607920bde8cafd2eb5587bd7a26f89ba0b5",
            },
            "arm64": {
                "name": "opencode-linux-arm64.tar.gz",
                "sha256sum": "3557e87db8c7db70e8ebd42157df1246554120896b115c462b760ff248cf751e",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["opencode"],
        present=not teardown,
    )

    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall OpenChamber",
        casks=["openchamber"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    binary = OpenCode(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{remote_home}/.local/bin/opencode",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("OpenCode")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
