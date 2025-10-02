from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from myinfra.operations import files as myfiles


## https://github.com/Wilfred/difftastic/releases
class Difftastic:
    version = "0.65.0"

    class Linux:
        sha256sum = "1de384a69813b665e36a816f24ff4bbad15059006996a69cdf677c997a6bd5b0"


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
def apply_difft(teardown=False):
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=f"https://github.com/Wilfred/difftastic/releases/download/{Difftastic.version}/difft-x86_64-unknown-linux-gnu.tar.gz",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/difft",
        sha256sum=Difftastic.Linux.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    apply_difft(teardown=teardown)


@deploy("Config")
def apply_config(teardown=False):
    myfiles.template(
        name=f"{'Remove ' if teardown else ''}.gitconfig",
        src="templates/git/.gitconfig.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.gitconfig",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        git_gpgsign=host.data.get("git_gpgsign", False),
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}.gitignore_global",
        src="files/git/.gitignore_global",
        dest=f"{host.get_fact(server_facts.Home)}/.gitignore_global",
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
        apply_linux(teardown=teardown)

    apply_config(teardown=teardown)


apply()
