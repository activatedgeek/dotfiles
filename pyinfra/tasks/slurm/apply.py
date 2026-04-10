from myinfra.facts import slurm as slurm_facts
from myinfra.operations import files as myfiles
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts

from pyinfra import host


@deploy("NVDA")
def apply_nvda(teardown=False):
    is_slurm_host = bool(host.get_fact(slurm_facts.SbatchBinary))

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}srun-docker",
        src="tasks/slurm/files/srun-docker",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/srun-docker",
        mode=755,
        create_remote_dir=False,
        present=is_slurm_host and not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    sbatch_bin = host.get_fact(slurm_facts.SbatchBinary)

    remote_home = host.get_fact(server_facts.Home)

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="tasks/slurm/files/.slurm_profile",
        dest=f"{remote_home}/.local/profile/.slurm_profile",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Aliases",
        src="tasks/slurm/templates/.slurm_aliases.j2",
        dest=f"{remote_home}/.local/profile/.slurm_aliases",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        sbatch_account=host.data.sbatch_account,
        sbatch_partitions=host.data.sbatch_partitions,
        sbatch_params=host.data.get("sbatch_params", {}),
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}sbatch",
        src="tasks/slurm/templates/sbatch.j2",
        dest=f"{remote_home}/.local/bin/sbatch",
        mode=755,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        sbatch_bin=sbatch_bin,
    )

    # if "nvda" in host.groups:
    #     apply_nvda(teardown=teardown)


@deploy("Slurm")
def apply():
    teardown = host.data.get("teardown", False)
    sbatch_bin = host.get_fact(slurm_facts.SbatchBinary)
    is_slurm_host = bool(sbatch_bin)
    if is_slurm_host:
        apply_config(teardown=teardown)
