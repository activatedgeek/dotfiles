from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, brew
from pyinfra.facts import server as server_facts


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall SSHPass",
        packages=["sshpass"],
        present=not teardown,
    )


@deploy("Home")
def apply_config_home(teardown=False):
    if teardown:
        files.directory(
            name="Delete",
            path=f"{host.get_fact(server_facts.Home)}/.ssh/config.d/nyu",
            present=False,
        )
    else:
        files.sync(
            name="Sync",
            src="files/ssh/nyu",
            dest=f"{host.get_fact(server_facts.Home)}/.ssh/config.d/nyu",
            dir_mode=700,
            mode=600,
            delete=True,
        )

    files.line(
        name="Include",
        path=f"{host.get_fact(server_facts.Home)}/.ssh/config",
        line="Include config.d/nyu/config",
        present=not teardown,
    )

    files.directory(
        name="Directory",
        path=f"{host.get_fact(server_facts.Home)}/.config/nyu",
        present=not teardown,
    )

    if host.data.get("nyu_pass", None):
        files.line(
            name="SSH Password",
            path=f"{host.get_fact(server_facts.Home)}/.config/nyu/pass",
            line=host.data.nyu_pass,
            present=not teardown,
        )

        files.file(
            name="Permissions",
            path=f"{host.get_fact(server_facts.Home)}/.config/nyu/pass",
            mode=600,
            present=not teardown,
        )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name="Config Dir.",
        path=f"{host.get_fact(server_facts.Home)}/.ssh/config.d",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    if host.data.get("org", "") == "me":
        apply_config_home(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)

    apply_config(teardown=teardown)


apply()
