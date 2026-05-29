from myinfra.operations import files as myfiles
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts

from pyinfra import host, inventory


@deploy("NVDA")
def apply_nvda(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    slurm_hosts = {
        f"{ihost.name.split('/')[-1]}": {
            "aliases": ihost.data.get("ssh_aliases"),
            "ssh_user": ihost.data.ssh_user,
            "sbatch_account": ihost.data.sbatch_account,
            "sbatch_partitions": ihost.data.sbatch_partitions,
        }
        for ihost in inventory.get_group("slurm")
        if not ihost.data.get("skip_host", False)
    }

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Hosts Conf",
        src="tasks/slurm_compose/templates/hosts.toml.j2",
        dest=f"{remote_home}/.config/slurm-compose/hosts.toml",
        mode=600,
        present=not teardown,
        ## Jinja2 Variables.
        hosts=slurm_hosts,
    )


@deploy("Config")
def apply_config(teardown=False):
    if "nvda" in host.groups:
        if any(k in host.groups for k in ["mac", "desktop"]):
            apply_nvda(teardown=teardown)


@deploy("Slurm Compose")
def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)
