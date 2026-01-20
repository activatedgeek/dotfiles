from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/starship/starship/releases
@dataclass
class Starship(Binary):
    version: ClassVar[str] = "1.24.2"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/starship/starship/releases/download/v{self.version}/starship-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "2a24f4deaf7a2b27e441cafe259251742b5e4bdc3011e3fc654dc657d7c45c33",
            },
            "arm64": {
                "src": f"https://github.com/starship/starship/releases/download/v{self.version}/starship-aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "559701ab549aad99c5f62ca74a65b7a5258f9c8371d5a7a6af6ef905b632ec48",
            },
        }


@deploy("Config")
def apply_config(teardown=False):
    myfiles.copy(
        name="Settings",
        src="files/starship/starship.toml",
        dest=f"{host.get_fact(server_facts.Home)}/.config/starship.toml",
        present=not teardown,
        mode=600,
        create_remote_dir=False,
    )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["starship"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    binary = Starship(arch)
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/starship",
        sha256sum=binary.sha256sum,
        present=not teardown,
        mode=755,
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
