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
    version: ClassVar[str] = "2.8.1-1"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "micromamba-linux-64",
                "sha256sum": "77b7790ec97f64581118f103585b175df4306f95829b0fa6bfe4a19cc88a1182",
            },
            "arm64": {
                "name": "micromamba-linux-aarch64",
                "sha256sum": "49aa29008cafa6cd6027ebd643fc43ca32c20740e60b0a05378c4e5bb837c217",
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
