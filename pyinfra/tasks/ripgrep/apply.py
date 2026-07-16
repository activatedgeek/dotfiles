from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from pyinfra import host


@dataclass
class RipGrep(Binary):
    gh_repo: ClassVar[str] = "BurntSushi/ripgrep"
    version: ClassVar[str] = "15.2.0"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": f"ripgrep-{self.version}-x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "e62198eb19b136b88c330af83647b5a962cb99b6b1f066758568f12de1974849",
            },
            "arm64": {
                "name": f"ripgrep-{self.version}-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "e36d0eb52e70696bdf1781392722e05a21bb91d3b7b762ef5ec20e5df2ec687b",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["ripgrep"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    binary = RipGrep(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        src_dir=Path(Path(binary.src).stem).stem,
        dest=f"{remote_home}/.local/bin/rg",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("RipGrep")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
