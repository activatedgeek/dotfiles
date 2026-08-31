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
    version: ClassVar[str] = "0.12.7"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "8264360c1b0a6f3df3d31620942216f57bba860179a2fc0916af1e5cf87c0d52",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "a42eb41171e452acb03eb03e4901484ca55c991cf178cb5907939dd80c2d9ac8",
            },
        }


@dataclass
class Uvx(Uv):
    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "459528549fb6ecc4f4b8f3276b64a108557ef55b68451a21b84007e502c153b2",
            },
            "arm64": {
                "name": "uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "4b4560c222f57067ab947f0bdc11f9f2167d1741b3814daf6f65aa5e22c78f68",
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
