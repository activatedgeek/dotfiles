from dataclasses import dataclass
from typing import ClassVar

from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from pyinfra import host


@dataclass
class Codex(Binary):
    gh_repo: ClassVar[str] = "openai/codex"
    version: ClassVar[str] = "rust-v0.147.0"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "codex-package-x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "cb0a15567e9a60a5820d54b0f6ae86d504dc3805c1eab21a47f70e3eb7b73a40",
            },
            "arm64": {
                "name": "codex-package-aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "e23d0be344d2496986c985cd3db61e6f649b1ddd900e6afc1b5aaabbffcbb4e2",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["codex", "chatgpt"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)
    binary = Codex(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        src_dir="bin",
        dest=f"{remote_home}/.local/bin/codex",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("Codex")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    ##
    # FIXME: Remote support is not great.
    #
    # elif kernel == "Linux":
    #     arch = host.get_fact(myserver_facts.DpkgArch)
    #     apply_linux(arch, teardown=teardown)


def pre_check():
    return "slurm" not in host.groups
