from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://github.com/ClementTsang/bottom/releases
class Btm:
    version = "0.10.2"

    class Linux:
        sha256sum = "b9c9a7bcb8a7056471700428357604643a37ca174ad1833cbbc45c31aff48a67"


@deploy("Linux")
def apply_linux(teardown=False):
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=f"https://github.com/ClementTsang/bottom/releases/download/{Btm.version}/bottom_x86_64-unknown-linux-musl.tar.gz",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/btm",
        sha256sum=Btm.Linux.sha256sum,
        present=not teardown,
        mode=755,
    )


@deploy("Config")
def apply_config(teardown=False):
    if teardown:
        files.directory(
            name="Remove",
            path=f"{host.get_fact(server_facts.Home)}/.config/bottom",
            present=False,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        apply_linux(teardown=teardown)
        apply_config(teardown=teardown)


apply()
