from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files
from pyinfra.facts import server as server_facts


@deploy("NVDA")
def apply_config_nvda(teardown=False):
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
            delete=True,
        )

    files.line(
        name="Include",
        path=f"{host.get_fact(server_facts.Home)}/.ssh/config",
        line="Include config.d/nvda/config",
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

    if host.name == "@local" and host.data.get("org", "") == "nvda":
        apply_config_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
