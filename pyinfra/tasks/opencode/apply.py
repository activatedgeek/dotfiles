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
class OpenCode(Binary):
    gh_repo: ClassVar[str] = "anomalyco/opencode"
    version: ClassVar[str] = "v1.19.3"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "opencode-linux-x64-musl.tar.gz",
                "sha256sum": "132c231b3df1d10c4d58d0db65d2ef660ce77c47b7dd3fa918efcc12a17ec8cb",
            },
            "arm64": {
                "name": "opencode-linux-arm64-musl.tar.gz",
                "sha256sum": "37c7de554c2ba7bf456e4fe6faf7705141b0ccb3a7b1dd6e1046d52cd8269ecd",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["anomalyco/tap/opencode-v2"],
        present=not teardown,
    )

    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall OpenChamber",
        casks=["openchamber"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    ## Temporarily disable until 2.0 releases on Github.
    # binary = OpenCode(arch)

    # myfiles.download(
    #     name=f"{'Uni' if teardown else 'I'}nstall",
    #     src=binary.src,
    #     dest=f"{remote_home}/.local/bin/opencode",
    #     sha256sum=binary.sha256sum,
    #     mode=755,
    #     present=not teardown,
    # )

    files.directory(
        name="systemd User Units",
        path=f"{remote_home}/.config/systemd/user",
        mode=700,
        recursive=True,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}OpenChamber Service",
        src="tasks/opencode/files/openchamber.service",
        dest=f"{remote_home}/.config/systemd/user/openchamber.service",
        mode=600,
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Config",
        src="tasks/opencode/files/opencode.json",
        dest=f"{remote_home}/.config/opencode/opencode.json",
        mode=600,
        present=not teardown,
    )


@deploy("OpenCode")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)
