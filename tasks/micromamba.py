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
    version: ClassVar[str] = "2.4.0-1"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/mamba-org/micromamba-releases/releases/download/{self.version}/micromamba-linux-64",
                "sha256sum": "6b64c543743b3fc680a8138fb0ed962d9c9066af5859c29b86f1ce04bed40b76",
            },
            "arm64": {
                "src": f"https://github.com/mamba-org/micromamba-releases/releases/download/{self.version}/micromamba-linux-aarch64",
                "sha256sum": "cbc9b04dbe48a096c6dc68d2c7cf0888021933c3f7c2c00b78e62bef4954d474",
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
        src="files/micromamba/.mm_profile",
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
