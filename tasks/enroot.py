from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files
from pyinfra.facts import server as server_facts


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name="Config Dir.",
        path=f"{host.get_fact(server_facts.Home)}/.config/enroot",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    files.line(
        name=f"{'Remove ' if teardown else ''}Creds.",
        path=f"{host.get_fact(server_facts.Home)}/.config/enroot/.credentials",
        line=f"machine gitlab-master.nvidia.com login {host.data.enroot_user} password {host.data.enroot_pass}",
        ensure_newline=True,
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        apply_config(teardown=teardown)


if all([host.data.get(k, "") for k in ["enroot_user", "enroot_pass"]]):
    apply()
