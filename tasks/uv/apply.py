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
    version: ClassVar[str] = "0.10.4"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "ae65ed04fee535f3ab8d31da7c2f9fde156dc5afdd6b5b5125e535ccc49bba34",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "bc4c9eaa140af1434c635d12aea2de2567c226805703f22178e0231a6e729478",
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
                "sha256sum": "dd061698c525ceded1660d5764b8def3275cb4c5e459e56a24fa5a7d685a782a",
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
