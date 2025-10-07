from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary


## https://github.com/mamba-org/micromamba-releases/releases
@dataclass
class Micromamba(Binary):
    version: ClassVar[str] = "2.3.2-0"

    @property
    def _arch_map(self):
        return {
            "x86_64": {
                "src": f"https://github.com/mamba-org/micromamba-releases/releases/download/{self.version}/micromamba-linux-64",
                "sha256sum": "ffc3cb8d52d4d6b354bdbb979c407719c485392b74e462cbd50811aa88e58f85",
            },
            "aarch64": {
                "src": f"https://github.com/mamba-org/micromamba-releases/releases/download/{self.version}/micromamba-linux-aarch64",
                "sha256sum": "7154d66112a623d8d930f8aab467347971d5c1403a84b1c25d19298f4fb9da03",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["micromamba"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall micromamba",
            path=f"{remote_home}/.local/bin/micromamba",
            present=False,
        )
    else:
        binary = Micromamba(arch)
        files.download(
            name="micromamba",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/micromamba",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name="Remove",
        path=f"{host.get_fact(server_facts.Home)}/.mamba",
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    # if kernel == "Darwin":
    #     apply_macos(teardown=teardown)
    if kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)


apply()
