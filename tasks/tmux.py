from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


@deploy("Config")
def apply_config(teardown=False):
    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Config",
        src="files/tmux/.tmux.conf",
        dest=f"{host.get_fact(server_facts.Home)}/.tmux.conf",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        apply_config(teardown=teardown)


apply()
