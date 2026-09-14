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
    version: ClassVar[str] = "0.12.13"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "b59310db262709ee92baf7954ef30820f1442ffa48b263f7001a236fe9004047",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "a5183e9245620e89b715a51b245f128a4e5d776dd715aea6086713373b9a88ee",
            },
        }


@dataclass
class Uvx(Uv):
    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "aa106f3652c36c4510c429ab62e9271a85ac124c3b70c0f5d7397e9a76a823c5",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "1720c6a91a473cc1bde35556fd45bcd2203b98523ea7b16f0b20378397853a04",
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
