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
    version: ClassVar[str] = "rust-v0.149.1"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "codex-package-x86_64-unknown-linux-musl.tar.gz",
                "sha256sum": "73dc5888888f411c1f0fa7b81d866e721dcc86b527ce8e3b2cf4708661e823ba",
            },
            "arm64": {
                "name": "codex-package-aarch64-unknown-linux-musl.tar.gz",
                "sha256sum": "2447e3fef519401ff6d6e90759ab1bf66082da48966fc6e4fe9a77108f9c20d8",
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
