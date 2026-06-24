from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@dataclass
class Yq(Binary):
    gh_repo: ClassVar[str] = "mikefarah/yq"
    version: ClassVar[str] = "v4.53.3"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "yq_linux_amd64",
                "sha256sum": "fa52a4e758c63d38299163fbdd1edfb4c4963247918bf9c1c5d31d84789eded4",
            },
            "arm64": {
                "name": "yq_linux_arm64",
                "sha256sum": "578648e463a11c1b6db6010cbf41eafed6bee79466fcffa1bb446672cf7945ea",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["yq"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall",
            path=f"{remote_home}/.local/bin/yq",
            present=False,
        )
    else:
        binary = Yq(arch)

        files.download(
            name="Install",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/yq",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("Yq")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
