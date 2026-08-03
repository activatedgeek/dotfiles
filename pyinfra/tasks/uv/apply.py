from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@dataclass
class Uv(Binary):
    gh_repo: ClassVar[str] = "astral-sh/uv"
    version: ClassVar[str] = "0.12.1"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "92face6b1f0462ad911857957bd168cd4ae45515e2a2cb3fcc3ecbda3d4d82b1",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "d8e93d894c81ebaa27ef159a5c5b1398283e30fdf91f662433caa494fa421b9f",
            },
        }


@dataclass
class Uvx(Uv):
    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "198b21110cb98998c515e25740e80bfa0bf3a437d7f6b0f7a098bfc90c07c442",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "1fe2f6a05b6e9d8e81dfdb101e9d76927550f2ade5ce4a2a15a0f63acf186d89",
            },
        }


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


@deploy("Uv")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
