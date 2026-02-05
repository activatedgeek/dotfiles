from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/astral-sh/uv/releases
@dataclass
class Uv(Binary):
    version: ClassVar[str] = "0.9.26"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "0650696de7f403348e9dd617e1f65dc32147c106c40129138017efd8f0f01cc8",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "70e124c01c543aa444ca2e647c00eee7b31ddcb0784bd6ede6910b539b6ef98b",
            },
        }

    @property
    def src_dir(self):
        return Path(self.src.removesuffix(".tar.gz")).stem


@dataclass
class Uvx(Uv):
    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "f28f05593cab3bf0a84fad73eae7322f1f18463e9f238a06201ef8d8a29a5a2c",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "8f03c3aca204b4fca4c2bebe033eda1cf7f5321876ece79d25fb5ca1e84a9197",
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
            src_dir=binary.src_dir,
            dest=f"{remote_home}/.local/bin/uv",
            sha256sum=binary.sha256sum,
            present=not teardown,
            mode=755,
        )

        binary = Uvx(arch)
        myfiles.download(
            name=f"{'Uni' if teardown else 'I'}nstall uvx",
            src=binary.src,
            src_dir=binary.src_dir,
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
