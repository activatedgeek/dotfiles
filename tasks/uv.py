from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew, files
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://github.com/astral-sh/uv/releases
uv_version = "0.4.0"


@deploy("Linux")
def apply_linux(teardown=False):
    if teardown:
        files.file(
            name="Uninstall uv",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/uv",
            present=False,
        )
        files.file(
            name="Uninstall uvx",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/uvx",
            present=False,
        )
    else:
        myfiles.download(
            name=f"{'Uni' if teardown else 'I'}nstall",
            src=f"https://github.com/astral-sh/uv/releases/download/{uv_version}/uv-x86_64-unknown-linux-gnu.tar.gz",
            src_dir="uv-x86_64-unknown-linux-gnu",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/uv",
            present=not teardown,
            mode=755,
        )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["uv"],
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        apply_linux(teardown=teardown)


apply()
