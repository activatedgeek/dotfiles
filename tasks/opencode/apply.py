from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/anomalyco/opencode/releases
@dataclass
class OpenCode(Binary):
    version: ClassVar[str] = "1.2.15"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/anomalyco/opencode/releases/download/v{self.version}/opencode-linux-x64.tar.gz",
                "sha256sum": "741df4d63dff3e5e01063e0352db69a77d7f4e9f7878c0587cf69a142f378337",
            },
            "arm64": {
                "src": f"https://github.com/anomalyco/opencode/releases/download/v{self.version}/opencode-linux-arm64.tar.gz",
                "sha256sum": "711f5902a2dabfb1e7d831b21f91e47ab6286b58903ae95d1f35d40478cc9223",
            },
        }


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall",
            path=f"{remote_home}/.local/bin/opencode",
            present=False,
        )
    else:
        binary = OpenCode(arch)
        myfiles.download(
            name="Install",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/opencode",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("MacOS")
def apply_macos(teardown=False):
    ## NOTE(sanyamk): Always shows success even when already installed.
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["anomalyco/tap/opencode"],
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


apply()
