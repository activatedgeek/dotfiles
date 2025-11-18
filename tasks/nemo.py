from pathlib import Path

from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.operations import files as myfiles


@deploy("NeMo-Skills")
def apply_nemo_skills(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name="Config Dir.",
        path=f"{remote_home}/.config/nemo_skills/cluster_configs",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    local_cluster_hosts = {
        f"{ihost.name.split('/')[-1]}": {
            "ssh_user": ihost.data.ssh_user,
        }
        for ihost in inventory.get_group("desktop")
    }

    for cluster_name, values in local_cluster_hosts.items():
        myfiles.template(
            name=f"{'Remove ' if teardown else ''}{cluster_name} Cluster Config",
            src="templates/nemo/cluster_configs/local.yaml.j2",
            dest=f"{remote_home}/.config/nemo_skills/cluster_configs/{cluster_name}.yaml",
            mode=600,
            create_remote_dir=False,
            present=not teardown,
            ## Jinja2 Variables.
            **values,
        )

    slurm_cluster_hosts = {
        f"{ihost.name.split('/')[-1]}": {
            "ssh_user": ihost.data.ssh_user,
            "ssh_tunnel_host": ihost.data.ssh_hostname,
            "ssh_tunnel_port": ihost.data.get("ssh_port", 22),
            "sbatch_account": ihost.data.sbatch_account,
            "sbatch_partition": ihost.data.sbatch_partition,
            "disable_gpus_per_node": ihost.data.get("nemo_skills_disable_gpus_per_node"),
            "disable_cpu_partition": ihost.data.get("nemo_skills_disable_cpu_partition"),
        }
        for ihost in inventory.get_group("slurm")
    }

    for cluster_name, values in slurm_cluster_hosts.items():
        myfiles.template(
            name=f"{'Remove ' if teardown else ''}{cluster_name} Cluster Config",
            src="templates/nemo/cluster_configs/slurm.yaml.j2",
            dest=f"{remote_home}/.config/nemo_skills/cluster_configs/{cluster_name}.yaml",
            mode=600,
            create_remote_dir=False,
            present=not teardown,
            ## Jinja2 Variables.
            **values,
        )


@deploy("NVDA")
def apply_nvda(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if "linux" in host.groups:
        myfiles.copy(
            name=f"{'Remove ' if teardown else ''}NeMo-Skills Profile",
            src="files/nemo/.nemo_skills_profile",
            dest=f"{remote_home}/.local/profile/.nemo_skills_profile",
            mode=600,
            create_remote_dir=False,
            present=not teardown,
        )

        store_home = host.data.get("store_home")
        if store_home:
            store_home = store_home.replace("${USER}", host.data.ssh_user)
            if not store_home.startswith(remote_home):
                files.directory(
                    name=f"{'Remove ' if teardown else ''}.nemo_run Directory",
                    path=str(Path(store_home).parent / ".nemo_run"),
                    mode=700,
                    present=not teardown,
                )

                files.link(
                    name=f"{'Remove ' if teardown else ''}.nemo_run Symlink",
                    path=f"{remote_home}/.nemo_run",
                    target=str(Path(store_home).parent / ".nemo_run"),
                    present=not teardown,
                )

    if "desktop" in host.groups:
        apply_nemo_skills(teardown=teardown)


@deploy("Config")
def apply_config(teardown=False):
    if host.data.get("org", "") == "nvda":
        apply_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
