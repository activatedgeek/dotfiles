from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.operations import files as myfiles


@deploy("NVDA")
def apply_nvda(teardown=False):
    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}NeMo Profile",
        src="files/nemo/.nemo_profile",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.nemo_profile",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    # if "desktop" in host.groups:
    #     homedir = host.get_fact(server_facts.Home)

    #     myfiles.template(
    #         name=f"{'Remove ' if teardown else ''}Local Cluster Config",
    #         src="templates/nemo/cluster_configs/local.yaml.j2",
    #         dest=f"{host.get_fact(server_facts.Home)}/.config/nemo/cluster_configs/local.yaml",
    #         mode=600,
    #         create_remote_dir=False,
    #         present=not teardown,
    #         ## Jinja2 Variables.
    #         store_home=host.data.get("store_home")
    #         .replace("${USER}", host.data.ssh_user)
    #         .replace("${HOME}", homedir),
    #     )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name="Config Dir.",
        path=f"{host.get_fact(server_facts.Home)}/.config/nemo/cluster_configs",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    if host.data.get("org", "") == "nvda":
        apply_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
