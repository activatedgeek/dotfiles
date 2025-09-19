from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts

from myinfra.facts import slurm as slurm_facts
from myinfra.operations import files as myfiles


@deploy("NVDA")
def apply_nvda(teardown=False):
    is_slurm_host = bool(host.get_fact(slurm_facts.SbatchExists))

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}srun-docker",
        src="files/slurm/srun-docker",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/srun-docker",
        mode=755,
        create_remote_dir=False,
        present=is_slurm_host and not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    is_slurm_host = bool(host.get_fact(slurm_facts.SbatchExists))

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="files/slurm/.slurm_profile",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.slurm_profile",
        mode=600,
        create_remote_dir=False,
        present=is_slurm_host and not teardown,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Env",
        src="templates/slurm/.slurm_env.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.slurm_env",
        mode=600,
        create_remote_dir=False,
        present=is_slurm_host and not teardown,
        ## Jinja2 Variables.
        sbatch_account=host.data.get("sbatch_account", None),
        sbatch_partition=host.data.get("sbatch_partition", None),
        sbatch_overcommit=host.data.get("sbatch_overcommit", None),
    )

    if host.data.get("org", "") == "nvda":
        apply_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
