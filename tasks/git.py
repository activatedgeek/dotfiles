from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://github.com/Wilfred/difftastic/releases
class Difftastic:
    version = "0.63.0"

    class Linux:
        sha256sum = "9d51d2a258b1a6cc1f6b1ed97e1961409d44c8f6fbae1f3947d9cdad76987307"


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
    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}.gitconfig",
        src="files/git/.gitconfig",
        dest=f"{host.get_fact(server_facts.Home)}/.gitconfig",
        present=not teardown,
        mode=600,
        create_remote_dir=False,
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
