from pyinfra import host, inventory
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.operations import files as myfiles


@deploy("Home")
def apply_config_home(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if host.name == "@local":
        if teardown:
            files.directory(
                name="Delete",
                path=f"{remote_home}/.ssh/config.d/home",
                present=False,
            )
        else:
            files.sync(
                name="Sync",
                src="tasks/ssh/files/home",
                dest=f"{remote_home}/.ssh/config.d/home",
                dir_mode=700,
                mode=600,
                delete=False,
            )

        files.line(
            name="Include",
            path=f"{remote_home}/.ssh/config",
            line="Include config.d/home/config",
            ensure_newline=True,
            present=not teardown,
        )


@deploy("NVDA")
def apply_config_nvda(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{remote_home}/.ssh/config.d/nvda",
        mode=700,
        present=not teardown,
    )

    if host.name == "@local" and not teardown:
        files.sync(
            name="Sync",
            src="tasks/ssh/files/nvda",
            dest=f"{remote_home}/.ssh/config.d/nvda",
            dir_mode=700,
            mode=600,
            delete=False,
            exclude=["*git*"],
        )

    slurm_hosts = {
        f"{ihost.name.split('/')[-1]}": {
            "hostname": ihost.data.ssh_hostname,
            "port": ihost.data.get("ssh_port", 22),
        }
        for ihost in inventory.get_group("slurm")
    }

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Config",
        src="tasks/ssh/templates/nvda/config.j2",
        dest=f"{remote_home}/.ssh/config.d/nvda/config",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        slurm_hosts=slurm_hosts,
        extended=(host.name == "@local"),
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

    if host.data.get("org") == "home":
        apply_config_home(teardown=teardown)
    elif host.data.get("org") == "nvda":
        apply_config_nvda(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
