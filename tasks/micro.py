from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.operations import files as myfiles


## https://github.com/zyedidia/micro/releases
class Micro:
    version = "2.0.14"

    class Linux:
        sha256sum = "26cab163197dd75207f7792c9ebf96ee1eb5c92b63af537ff9568eb2f8345b53"


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["micro"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=f"https://github.com/zyedidia/micro/releases/download/v{Micro.version}/micro-{Micro.version}-linux64-static.tar.gz",
        src_dir=f"micro-{Micro.version}",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/micro",
        sha256sum=Micro.Linux.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    if teardown:
        files.directory(
            name="Remove",
            path=f"{host.get_fact(server_facts.Home)}/.config/micro",
            present=False,
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
