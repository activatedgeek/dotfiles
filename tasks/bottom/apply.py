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
    version: ClassVar[str] = "0.12.3"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/ClementTsang/bottom/releases/download/{self.version}/bottom_x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "815da63fa6ef651fb4841bf0bf5efb54a2cbd6e3fdce80a139ed0bc7d4d27a6a",
            },
            "arm64": {
                "src": f"https://github.com/ClementTsang/bottom/releases/download/{self.version}/bottom_aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "822490a5f44d5f8f370c2a2036f51866ff17a53baee488f573e738a1be647524",
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
