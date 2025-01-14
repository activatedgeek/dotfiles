from pyinfra import host, local
from pyinfra.api import deploy
from pyinfra.operations import brew, files
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["ghostty"],
        present=not teardown,
    )

    local.include("tasks/fontconfig.py")


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{host.get_fact(server_facts.Home)}/.config/ghostty",
        present=not teardown,
        mode=700,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Options",
        src="files/ghostty/config",
        dest=f"{host.get_fact(server_facts.Home)}/.config/ghostty/config",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
        apply_config(teardown=teardown)


apply()
