from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/ClementTsang/bottom/releases
@dataclass
class Btm(Binary):
    version: ClassVar[str] = "0.11.1"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/ClementTsang/bottom/releases/download/{self.version}/bottom_x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "ff67e8ecd567c98bbb4016defd4efd8090e9b6a926a3c72cab184e73c964f0a9",
            },
            "arm64": {
                "src": f"https://github.com/ClementTsang/bottom/releases/download/{self.version}/bottom_aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "d8bf90b6058edf14118eb12fa3b86070386b7376bce08df72a96f5737647b737",
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


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
        apply_config(teardown=teardown)


apply()
