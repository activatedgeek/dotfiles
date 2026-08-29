from myinfra.operations import files as myfiles
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from pyinfra import host


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["paseo"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name="systemd User Units",
        path=f"{remote_home}/.config/systemd/user",
        mode=700,
        recursive=True,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Paseo Service",
        src="tasks/paseo/files/paseo.service",
        dest=f"{remote_home}/.config/systemd/user/paseo.service",
        mode=600,
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Config",
        src="tasks/paseo/files/config.json",
        dest=f"{remote_home}/.paseo/config.json",
        mode=600,
        present=not teardown,
    )


@deploy("Paseo")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        apply_linux(teardown=teardown)

    apply_config(teardown=teardown)
