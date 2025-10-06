from dataclasses import dataclass
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
    version: ClassVar[str] = "0.8.22"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "a261804d9493a96e7eebf13bcffc1b7ecc87dbd7da9a2800af94c20182d1a70d",
            },
            "arm64": {
                "src": f"https://github.com/astral-sh/uv/releases/download/{self.version}/uv-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "774e2e7e95389267bb58383c9d2af3aa4a422c8d37cd684712772bbba5530c9a",
            },
        }


@deploy("Linux")
def apply_linux(arch, teardown=False):
    if teardown:
        files.file(
            name="Uninstall uv",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/uv",
            present=False,
        )
        files.file(
            name="Uninstall uvx",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/uvx",
            present=False,
        )
    else:
        binary = Uv(arch)
        myfiles.download(
            name=f"{'Uni' if teardown else 'I'}nstall",
            src=binary.src,
            src_dir=f"uv-{arch}-unknown-linux-gnu",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/uv",
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
