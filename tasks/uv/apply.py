from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


@dataclass
class Uv(Binary):
    gh_repo: ClassVar[str] = "astral-sh/uv"
    version: ClassVar[str] = "0.10.9"
    asset_map: ClassVar[dict[str, dict[str, str]]] = field(
        default_factory=lambda: {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "8f8aa2a27b00bf3b35880b2e943bb8fd58714abe0981f8467b90e75faab41131",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "2452f3680578ab0e1bee5e035dcac2486445770ac4ccc98cefc743c5740c352f",
            },
        }
    )


@dataclass
class Uvx(Uv):
    asset_map: ClassVar[dict[str, dict[str, str]]] = field(
        default_factory=lambda: {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "f970b2576b7ae459afe8be1826f9812ddd5fa431a9ddfea155fae52e7443ac74",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "6fa59bc46bffff8ea41dfb21ea9c82d38928c539b2a5688cbdb29cd518e1c09b",
            },
        }
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall uv",
            path=f"{remote_home}/.local/bin/uv",
            present=False,
        )
        files.file(
            name="Uninstall uvx",
            path=f"{remote_home}/.local/bin/uvx",
            present=False,
        )
    else:
        binary = Uv(arch)
        myfiles.download(
            name=f"{'Uni' if teardown else 'I'}nstall uv",
            src=binary.src,
            src_dir=Path(binary.src.removesuffix(".tar.gz")).stem,
            dest=f"{remote_home}/.local/bin/uv",
            sha256sum=binary.sha256sum,
            present=not teardown,
            mode=755,
        )

        binary = Uvx(arch)
        myfiles.download(
            name=f"{'Uni' if teardown else 'I'}nstall uvx",
            src=binary.src,
            src_dir=Path(binary.src.removesuffix(".tar.gz")).stem,
            dest=f"{remote_home}/.local/bin/uvx",
            sha256sum=binary.sha256sum,
            present=not teardown,
            mode=755,
        )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["uv"],
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
