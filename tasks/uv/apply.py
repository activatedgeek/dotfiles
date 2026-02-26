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
    version: ClassVar[str] = "0.10.6"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "1cec0cda74b129b3e15ed7ff80d0ce303c5e3446cd0dbc47675e908052587419",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "7644a9b798e80c5b448c212d5051435ca978d3fc2210c6be9c0af7f997108ef7",
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
                "sha256sum": "2037193e82ecb74eaa503536da780098b4ab5512b44726d231b9247b8a3be182",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "aec87f57554961a48905d0fea7e9486c30bd8750755d42760464b4eacac47fed",
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
