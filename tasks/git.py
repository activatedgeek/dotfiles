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
    version: ClassVar[str] = "0.65.0"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/Wilfred/difftastic/releases/download/{self.version}/difft-x86_64-unknown-linux-gnu.tar.gz",
                "sha256sum": "1de384a69813b665e36a816f24ff4bbad15059006996a69cdf677c997a6bd5b0",
            },
            "arm64": {
                "src": f"https://github.com/Wilfred/difftastic/releases/download/{self.version}/difft-aarch64-unknown-linux-gnu.tar.gz",
                "sha256sum": "a3fc036c2e5b6d5680be047cd3ec49812139004fc46b2455030b0c2f00891222",
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
        src="templates/git/.gitconfig.j2",
        dest=f"{remote_home}/.gitconfig",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        git_gpgsign=host.data.get("git_gpgsign", False),
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}.gitignore_global",
        src="files/git/.gitignore_global",
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
