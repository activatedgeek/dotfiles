from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.operations import files as myfiles


@deploy("NVDA")
def apply_config_nvda(teardown=False):
    if host.name in ["@local", "@ssh/desk"]:
        if teardown:
            files.directory(
                name="Delete",
                path=f"{host.get_fact(server_facts.Home)}/.ssh/config.d/nvda",
                present=False,
            )
        else:
            files.sync(
                name="Sync",
                src="files/ssh/nvda",
                dest=f"{host.get_fact(server_facts.Home)}/.ssh/config.d/nvda",
                dir_mode=700,
                mode=600,
                delete=False,
            )

    if host.name == "@local":
        myfiles.template(
            name=f"{'Remove ' if teardown else ''}Config",
            src="templates/ssh/nvda/config.j2",
            dest=f"{host.get_fact(server_facts.Home)}/.ssh/config.d/nvda/config",
            mode=600,
            create_remote_dir=False,
            present=not teardown,
        )

        files.line(
            name="Include",
            path=f"{host.get_fact(server_facts.Home)}/.ssh/config",
            line="Include config.d/nvda/config",
            ensure_newline=True,
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

    if host.data.get("org", "") == "nvda":
        apply_config_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
