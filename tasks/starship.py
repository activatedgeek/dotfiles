from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://github.com/starship/starship/releases
class Starship:
    version = "1.22.1"

    class Linux:
        sha256sum = "08eb5b058e95358a62ff986f273b6b3d8264f7fc5f3889a21a3a99f1955b3388"


@deploy("Config")
def apply_config(teardown=False):
    myfiles.copy(
        name="Settings",
        src="files/starship/starship.toml",
        dest=f"{host.get_fact(server_facts.Home)}/.config/starship.toml",
        present=not teardown,
        mode=600,
        create_remote_dir=False,
    )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["starship"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=f"https://github.com/starship/starship/releases/download/v{Starship.version}/starship-x86_64-unknown-linux-gnu.tar.gz",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/starship",
        sha256sum=Starship.Linux.sha256sum,
        present=not teardown,
        mode=755,
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
