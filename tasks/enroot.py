from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

import myinfra.facts.enroot as enroot_facts
import myinfra.operations.files as myfiles


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name="Config Dir.",
        path=f"{host.get_fact(server_facts.Home)}/.config/enroot/mounts.d",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="files/enroot/.credentials",
        dest=f"{host.get_fact(server_facts.Home)}/.config/enroot/.credentials",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}mkenroot",
        src="files/enroot/mkenroot.sh",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/mkenroot",
        mode=755,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''} Default Mounts",
        src="templates/enroot/mounts.d/default.fstab.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.config/enroot/mounts.d/default.fstab",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        store_home=host.data.store_home,
        extra_mounts=host.data.get("enroot_mounts", []),
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    enroot_exists = host.get_fact(enroot_facts.EnrootExists)
    if kernel == "Linux" and enroot_exists:
        apply_config(teardown=teardown)


apply()
