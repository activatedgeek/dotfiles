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
    version: ClassVar[str] = "15.1.0"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": f"ripgrep-{self.version}-x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "ebeaf56f8a25e102e9419933423738b3a2a613a444fd749d695e15eba53f71f2",
            },
            "arm64": {
                "name": f"ripgrep-{self.version}-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "968cabe8efed72fd8fd482cb76b6084fcb695fc5293af7fb62296b02f487fb69",
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
