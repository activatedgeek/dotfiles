from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


@deploy("NYU")
def apply_nyu(teardown=False):
    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="files/slurm/.slurm_profile",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.slurm_profile",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}srun-docker",
        src="files/slurm/srun-docker",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/srun-docker",
        mode=755,
        create_remote_dir=False,
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)

    if host.data.get("slurm_host", False):
        if host.data.get("org", "") == "nyu":
            apply_nyu(teardown=teardown)


apply()
