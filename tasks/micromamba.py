from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew, files
from pyinfra.facts import server as server_facts


## https://github.com/mamba-org/micromamba-releases/releases
class Micromamba:
    version = "2.3.0-1"

    class Linux:
        sha256sum = "83f38b81295dade6b242b40dbab81bcd9fb03bb196928ab15f552cbafe82386b"


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["micromamba"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    if teardown:
        files.file(
            name="Uninstall micromamba",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/micromamba",
            present=False,
        )
    else:
        files.download(
            name="micromamba",
            src=f"https://github.com/mamba-org/micromamba-releases/releases/download/{Micromamba.version}/micromamba-linux-64",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/micromamba",
            sha256sum=Micromamba.Linux.sha256sum,
            mode=755,
        )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name="Remove",
        path=f"{host.get_fact(server_facts.Home)}/.mamba",
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    # if kernel == "Darwin":
    #     apply_macos(teardown=teardown)
    if kernel == "Linux":
        apply_linux(teardown=teardown)


apply()
