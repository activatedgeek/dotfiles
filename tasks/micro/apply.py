from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/zyedidia/micro/releases
@dataclass
class Micro(Binary):
    version: ClassVar[str] = "2.0.15"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/zyedidia/micro/releases/download/v{self.version}/micro-{self.version}-linux64-static.tar.gz",
                "sha256sum": "2027f2e4698fa4e826523ad16b95c724bf808de479f10ec769cdd200437701b3",
            },
            "arm64": {
                "src": f"https://github.com/zyedidia/micro/releases/download/v{self.version}/micro-{self.version}-linux-arm64.tar.gz",
                "sha256sum": "e0b4a8234f0432474e7ee28e12ffac0fe3bd31f030ba51dc059caa2f3d6d8bfc",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["micro"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    binary = Micro(arch)
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        src_dir=f"micro-{binary.version}",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/micro",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    if teardown:
        files.directory(
            name="Remove",
            path=f"{host.get_fact(server_facts.Home)}/.config/micro",
            present=False,
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
