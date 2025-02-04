from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew, files
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://github.com/astral-sh/uv/releases
class Uv:
    version = "0.5.27"

    class Linux:
        sha256sum = "16b9772ce5b57e00c92dfe4283c02e3ebefd78f8a9caa9d3f9778797633c8f75"


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
            src=f"https://github.com/astral-sh/uv/releases/download/{Uv.version}/uv-x86_64-unknown-linux-gnu.tar.gz",
            src_dir="uv-x86_64-unknown-linux-gnu",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/uv",
            sha256sum=Uv.Linux.sha256sum,
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
