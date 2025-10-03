from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/starship/starship/releases
@dataclass
class Starship(Binary):
    version: ClassVar[str] = "1.23.0"

    @property
    def _arch_map(self):
        return {
            "x86_64": {
                "src": f"https://github.com/starship/starship/releases/download/v{self.version}/starship-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "a66fd858b373c233b97564d22a29823d2dfa6e5f550585a5440a56da1250baa0",
            },
            "aarch64": {
                "src": f"https://github.com/starship/starship/releases/download/v{self.version}/starship-aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "d5a99287178b42e1e76f81627cabaf4f49a3575fb223dfa3aebd70420a58e1fd",
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
        arch = host.get_fact(server_facts.Arch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)


apply()
