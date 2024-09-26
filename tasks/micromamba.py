from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew, files
from pyinfra.facts import server as server_facts


## https://github.com/mamba-org/micromamba-releases/releases
micromamba_version = "1.5.8-0"


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
            name="Uninstall",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/micromamba",
            present=False,
        )
    else:
        files.download(
            name="Install",
            src=f"https://github.com/mamba-org/micromamba-releases/releases/download/{micromamba_version}/micromamba-linux-64",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/micromamba",
            mode=755,
        )


@deploy("Config")
def apply_config(teardown=False):
    if teardown:
        files.directory(
            name="Remove .conda",
            path=f"{host.get_fact(server_facts.Home)}/.conda",
            present=False,
        )
        files.directory(
            name="Remove .micromamba",
            path=f"{host.data.get('store_home', host.get_fact(server_facts.Home))}/.micromamba",
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
