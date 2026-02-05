from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.operations import files as myfiles


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["ghostty"],
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{remote_home}/.config/ghostty",
        present=not teardown,
        mode=700,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Options",
        src="tasks/ghostty/files/config",
        dest=f"{remote_home}/.config/ghostty/config",
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
