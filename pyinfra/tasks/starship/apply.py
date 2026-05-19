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
class Starship(Binary):
    gh_repo: ClassVar[str] = "starship/starship"
    version: ClassVar[str] = "v1.25.1"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "starship-x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "7692a9b84200e65b62670212e0f05eee00bdb77a39271ef60a3837f65bc00c3e",
            },
            "arm64": {
                "name": "starship-aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "a8dcb8c0caa6dd4e914ce511f5cd33cf52c38b1435146acf855e1f4d8aebdc9b",
            },
        }


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name="Config Dir.",
        path=f"{remote_home}/.config",
        mode=700,
        present=True,
        recursive=True,
    )

    myfiles.copy(
        name="Settings",
        src="tasks/starship/files/starship.toml",
        dest=f"{remote_home}/.config/starship.toml",
        present=not teardown,
        mode=600,
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


@deploy("Starship")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)
