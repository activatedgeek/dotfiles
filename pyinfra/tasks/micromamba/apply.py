from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@dataclass
class Micromamba(Binary):
    gh_repo: ClassVar[str] = "mamba-org/micromamba-releases"
    version: ClassVar[str] = "2.7.0-0"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "micromamba-linux-64",
                "sha256sum": "fb4554d61a1c567726890169e39c41aa8495dbba56f50957ee7356572b6c5726",
            },
            "arm64": {
                "name": "micromamba-linux-aarch64",
                "sha256sum": "a3678dd92f79e3f1a66ea2150696cf50bffc4d6b9d03b9d03a60bd1b4153f342",
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

    if teardown:
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
        present=not teardown,
    )


@deploy("Micromamba")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)


def pre_check():
    return False
