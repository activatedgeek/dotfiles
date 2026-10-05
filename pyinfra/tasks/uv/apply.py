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
    version: ClassVar[str] = "0.12.23"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "abdc39eab8b4ad341dca91f3823a23a343fae94bdb22ebdd9e91694415206f2f",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "ed797a095bf9aea58135fa7081c290e51a14cfd3a7b1f24e55cb1d1a0c1007b0",
            },
        }


@dataclass
class Uvx(Uv):
    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "452ed5ec13033e3930bcc75725e8e6bf11ec496d2f392e666893afdefdb9d775",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "3739b9e35a1be7e89c1d99c494e5de040e9e56b6973bb27627a12bd6699e4aa7",
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
