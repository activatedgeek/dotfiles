from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/mamba-org/micromamba-releases/releases
@dataclass
class Micromamba(Binary):
    version: ClassVar[str] = "2.5.0-2"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/mamba-org/micromamba-releases/releases/download/{self.version}/micromamba-linux-64",
                "sha256sum": "c04571cfb0750e5432d530a3068b8fcd232ebed3133358e056e59a90b9852b00",
            },
            "arm64": {
                "src": f"https://github.com/mamba-org/micromamba-releases/releases/download/{self.version}/micromamba-linux-aarch64",
                "sha256sum": "a64db0d7a82107c8d64357cf035fb8f9dbbe2fc48f48b302cbc8ba1590974e20",
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
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name="Remove",
        path=f"{remote_home}/.mamba",
        present=not teardown,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="tasks/micromamba/files/.mm_profile",
        dest=f"{remote_home}/.local/profile/.mm_profile",
        mode=600,
        create_remote_dir=False,
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
