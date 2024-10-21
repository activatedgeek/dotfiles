from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, brew
from pyinfra.facts import server as server_facts


## https://github.com/jqlang/jq/releases
class Jq:
    version = "1.7.1"

    class Linux:
        sha256sum = "5942c9b0934e510ee61eb3e30273f1b3fe2590df93933a93d7c58b81d19c8ff5"


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["jq"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    if teardown:
        files.file(
            name="Uninstall",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/jq",
            present=False,
        )
    else:
        files.download(
            name="Install",
            src=f"https://github.com/jqlang/jq/releases/download/jq-{Jq.version}/jq-linux64",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/jq",
            sha256sum=Jq.Linux.sha256sum,
            mode=755,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        apply_linux(teardown=teardown)


apply()
