from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from pyinfra import host


@dataclass
class Btm(Binary):
    gh_repo: ClassVar[str] = "ClementTsang/bottom"
    version: ClassVar[str] = "0.14.1"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "bottom_x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "31614bd39ad541b1c6096ba02fff6491bead2e45958e78b2fab343146d2e3635",
            },
            "arm64": {
                "name": "bottom_aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "b77f5977c1a63de6fe657feab9d03d761375735ece5e7aba53a794d6631752e8",
            },
        }


@deploy("Linux")
def apply_linux(arch, teardown=False):
    binary = Btm(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/btm",
        sha256sum=binary.sha256sum,
        present=not teardown,
        mode=755,
    )


@deploy("Config")
def apply_config(teardown=False):
    if teardown:
        files.directory(
            name="Remove",
            path=f"{host.get_fact(server_facts.Home)}/.config/bottom",
            present=False,
        )


@deploy("Bottom")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
        apply_config(teardown=teardown)
