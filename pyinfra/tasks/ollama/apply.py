from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from pyinfra import host


@dataclass
class Ollama(Binary):
    gh_repo: ClassVar[str] = "ollama/ollama"
    version: ClassVar[str] = "v0.19.0"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "ollama-linux-amd64.tar.zst",
                "sha256sum": "67d6bab88e63718d52782ee59db0e40436b35865f424b0ab13d9598e54d6e13a",
            },
            "arm64": {
                "name": "ollama-linux-arm64.tar.zst",
                "sha256sum": "259263d5ae0f8d716b9d8b199a137c9710ff348fa19dea0ce0120dc67735e171",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["ollama"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    binary = Ollama(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        src_dir="bin",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/ollama",
        sha256sum=binary.sha256sum,
        present=not teardown,
        mode=755,
    )


@deploy("Ollama")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
