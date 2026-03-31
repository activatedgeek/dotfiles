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
    version: ClassVar[str] = "v1.3.10"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "opencode-linux-x64.tar.gz",
                "sha256sum": "df0dfb4d696b414fc55183d194d07bb86e0145c9ac5862a17ba81703d1b444a1",
            },
            "arm64": {
                "name": "opencode-linux-arm64.tar.gz",
                "sha256sum": "a3b935cba3e24eb930cd060bdc4a3bb70e699e7412ff60d61fef5cdbef5ea9a7",
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
    ## @NOTE: Always shows success even when already installed.
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["anomalyco/tap/opencode"],
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name="Directory",
        path=f"{remote_home}/.config/opencode",
        mode=700,
        recursive=True,
        present=not teardown,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}opencode.json",
        src="tasks/opencode/files/opencode.json",
        dest=f"{remote_home}/.config/opencode/opencode.json",
        mode=600,
        create_remote_dir=False,
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
