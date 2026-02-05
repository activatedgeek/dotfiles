from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/Wilfred/difftastic/releases
@dataclass
class Difftastic(Binary):
    version: ClassVar[str] = "0.67.0"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/Wilfred/difftastic/releases/download/{self.version}/difft-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "865ef78b86eac72aa6440e380661b442244b58e02e333ad82df8e21a254d64a9",
            },
            "arm64": {
                "src": f"https://github.com/Wilfred/difftastic/releases/download/{self.version}/difft-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "c824e84555cd0eaace328ffe4c934053de4fa9763213fb8e47791fdf81d1ada5",
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
        ],
        present=not teardown,
    )


@deploy("difft")
def apply_difft(arch, teardown=False):
    ## FIXME(activatedgeek): <jemalloc>: Unsupported system page size
    if arch == "arm64":
        teardown = True

    binary = Difftastic(arch)
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/difft",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    apply_difft(arch, teardown=teardown)


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}.gitconfig",
        src="tasks/git/templates/.gitconfig.j2",
        dest=f"{remote_home}/.gitconfig",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        git_gpgsign=host.data.get("git_gpgsign", False),
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}.gitignore_global",
        src="tasks/git/files/.gitignore_global",
        dest=f"{remote_home}/.gitignore_global",
        present=not teardown,
        mode=600,
        create_remote_dir=False,
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
