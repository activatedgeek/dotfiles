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
    sbatch_bin = host.get_fact(slurm_facts.SbatchExists)
    is_slurm_host = bool(sbatch_bin)

    remote_home = host.get_fact(server_facts.Home)

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="files/slurm/.slurm_profile",
        dest=f"{remote_home}/.local/profile/.slurm_profile",
        mode=600,
        create_remote_dir=False,
        present=is_slurm_host and not teardown,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Env",
        src="templates/slurm/.slurm_env.j2",
        dest=f"{remote_home}/.local/profile/.slurm_env",
        mode=600,
        create_remote_dir=False,
        present=is_slurm_host and not teardown,
        ## Jinja2 Variables.
        sbatch_account=host.data.get("sbatch_account", None),
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}sbatch",
        src="templates/slurm/sbatch.j2",
        dest=f"{remote_home}/.local/bin/sbatch",
        mode=755,
        create_remote_dir=False,
        present=is_slurm_host and not teardown,
        ## Jinja2 Variables.
        sbatch_bin=sbatch_bin,
    )

    # if host.data.get("org", "") == "nvda":
    #     apply_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
