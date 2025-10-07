from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.operations import files as myfiles


@deploy("NVDA")
def apply_config_nvda(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if host.name == "@local" or "desktop" in host.groups:
        if teardown:
            files.directory(
                name="Delete",
                path=f"{remote_home}/.ssh/config.d/nvda",
                present=False,
            )
        else:
            files.sync(
                name="Sync",
                src="files/ssh/nvda",
                dest=f"{remote_home}/.ssh/config.d/nvda",
                dir_mode=700,
                mode=600,
                delete=False,
            )

    if host.name == "@local":
        slurm_hosts = {
            f"{ihost.name.split('/')[-1]}": {
                "ssh_hostname_format": ihost.data.ssh_hostname_format,
                "num_login_nodes": ihost.data.get("num_login_nodes", 0),
                "num_dc_nodes": ihost.data.get("num_dc_nodes", 0),
            }
            for ihost in inventory.get_group("slurm")
        }

        myfiles.template(
            name=f"{'Remove ' if teardown else ''}Config",
            src="templates/ssh/nvda/config.j2",
            dest=f"{remote_home}/.ssh/config.d/nvda/config",
            mode=600,
            create_remote_dir=False,
            present=not teardown,
            ## Jinja2 variables.
            slurm_hosts=slurm_hosts,
        )

        files.line(
            name="Include",
            path=f"{remote_home}/.ssh/config",
            line="Include config.d/nvda/config",
            ensure_newline=True,
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

    if host.data.get("org", "") == "nvda":
        apply_config_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
