from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@dataclass
class Mise(Binary):
    gh_repo: ClassVar[str] = "jdx/mise"
    version: ClassVar[str] = "v2026.3.18"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": f"mise-{self.version}-linux-x64",
                "sha256sum": "ef451d0af42443e20fed5d1952a33e9deb6cda8dc31cdc7d77d86fceddf91529",
            },
            "arm64": {
                "name": f"mise-{self.version}-linux-arm64",
                "sha256sum": "7c50f4fa3bf01234c801c77b99ef57f4f3d9add32f298ce40c95b31bdace2b3b",
            },
        }


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall mise",
            path=f"{remote_home}/.local/bin/mise",
            present=False,
        )
    else:
        binary = Mise(arch)

        files.download(
            name="mise",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/mise",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["mise"],
        present=not teardown,
    )


@deploy("Mise")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
