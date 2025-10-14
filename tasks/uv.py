from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.operations import uv as myuv
from myinfra.utils import Binary


## https://github.com/astral-sh/uv/releases
@dataclass
class Uv(Binary):
    version: ClassVar[str] = "0.9.2"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "b399aea47c961d15b83ae3ea14d616149a1babb157c53009b49a15ceafcc9fee",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "707e3c4cdb62789bb8b2c4072a26147f8f765b8082f75db6600eb83549dd9423",
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
                "sha256sum": "421b1bb58429180a04ade98da066b5a5b6763e8ed74edef97359701c4cb42db8",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "8e6e02c3f41124bf09c8ad9a1a89b7020a70f93ccc3d4b5c934b1052099d1b9e",
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


@deploy("NVDA")
def apply_nvda(teardown=False):
    remote_home = host.get_fact(server_facts.Home)
    store_home = host.data.store_home

    myuv.venv(
        name=f"{'Remove ' if teardown else ''}venv",
        path=f"{store_home}/uv",
        requirements=["apprise", "dvc"],
        binary_path=f"{remote_home}/.local/bin/uv",
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    if host.data.get("org", "") == "nvda":
        apply_nvda(teardown=teardown)


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
        apply_config(teardown=teardown)


apply()
