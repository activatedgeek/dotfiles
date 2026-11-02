from dataclasses import dataclass
from typing import ClassVar

import myinfra.facts.git as git_facts
from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from pyinfra import host


@dataclass
class Difftastic(Binary):
    gh_repo: ClassVar[str] = "Wilfred/difftastic"
    version: ClassVar[str] = "0.72.0"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "difft-0.72.0-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "c211db13c7aa131900585c949814fc2c42b9de65a9924eb988cb171da39a71aa",
            },
            ## FIXME(activatedgeek): <jemalloc>: Unsupported system page size
            "arm64": {
                "name": "difft-0.72.0-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "9f8daf1594e6edfcee812593fdc0c6fcb22ac0e07ca461a1b0ef2a1a877cabd4",
            },
        }


@dataclass
class Omnidiff(Binary):
    gh_repo: ClassVar[str] = "ivankovic/omnidiff"
    version: ClassVar[str] = "v0.3.0"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "omnidiff-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "457e786735a784fb04ea0baede43acf2491d18a80937d4a5df450b0ecd306eda",
            },
            "arm64": {
                "name": "omnidiff-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "70c0203d9d5f85982b38cfca58f225e3fec293287e6665a9414af55bd85e6b45",
            },
        }


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=[
            "git",
            "git-lfs",
            "difftastic",
            "ivankovic/omnidiff/omnidiff",
        ],
        present=not teardown,
    )


@deploy("difft")
def apply_difft(arch, teardown=False):
    binary = Difftastic(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/difft",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("omnidiff")
def apply_omnidiff(arch, teardown=False):
    binary = Omnidiff(arch)

    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/omnidiff",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    apply_difft(arch, teardown=teardown)
    apply_omnidiff(arch, teardown=teardown)


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}.gitignore_global",
        src="tasks/git/files/.gitignore_global",
        dest=f"{remote_home}/.gitignore_global",
        present=not teardown,
        mode=600,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}.gitconfig",
        src="tasks/git/templates/.gitconfig.j2",
        dest=f"{remote_home}/.gitconfig",
        mode=600,
        present=not teardown,
        ## Jinja2 Variables.
        git_name=host.get_fact(myserver_facts.UserFullName),
        git_email=host.data.email,
        git_xet=bool(host.get_fact(git_facts.GitXetBinary, path=f"{remote_home}/.local/bin/git-xet")),
    )


@deploy("Git")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)
