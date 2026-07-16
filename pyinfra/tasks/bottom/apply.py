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
    version: ClassVar[str] = "0.14.4"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "bottom_x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "901869a3ac781e63ae77c6dd834949f1aecdb3a4ee5f0ec2541093bcd55c4464",
            },
            "arm64": {
                "name": "bottom_aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "c3b30424e940b83a47bf1884e509b8cbe257395c2ef36e2e35d5d98d7c9b611f",
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
