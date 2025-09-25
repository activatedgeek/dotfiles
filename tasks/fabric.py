from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts

import myinfra.operations.files as myfiles


@deploy("NVDA")
def apply_nvda(teardown=False):
    if "desktop" in host.groups:
        myfiles.copy(
            name=f"{'Remove ' if teardown else ''}fabric.yaml",
            src="files/fabric/.fabric.yaml",
            dest=f"{host.get_fact(server_facts.Home)}/.fabric.yaml",
            mode=600,
            create_remote_dir=False,
            present=not teardown,
        )


@deploy("Config")
def apply_config(teardown=False):
    if host.data.get("org", "") == "nvda":
        apply_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
