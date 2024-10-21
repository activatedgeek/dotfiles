from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://github.com/Nukesor/pueue/releases
class Pueue:
    version = "3.4.1"

    class Linux:
        sha256sum = "2396dabbb9c7506ad120e1bce7d92c33917c6e5bb7d0a53e8d762d9d59d6b869"


class Pueued(Pueue):
    class Linux:
        sha256sum = "5f095cdf8c417def4bc29bf37b713e72a406ea3302d3e91f6a92d0398fe0c70d"


@deploy("Linux")
def apply_linux(teardown=False):
    if teardown:
        files.file(
            name="Uninstall pueue",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/pueue",
            present=False,
        )
        files.file(
            name="Uninstall pueued",
            path=f"{host.get_fact(server_facts.Home)}/.local/bin/pueued",
            present=False,
        )
    else:
        files.download(
            name="pueue",
            src=f"https://github.com/Nukesor/pueue/releases/download/v{Pueue.version}/pueue-linux-x86_64",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/pueue",
            sha256sum=Pueue.Linux.sha256sum,
            mode=755,
        )
        files.download(
            name="pueued",
            src=f"https://github.com/Nukesor/pueue/releases/download/v{Pueued.version}/pueued-linux-x86_64",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/pueued",
            sha256sum=Pueued.Linux.sha256sum,
            mode=755,
        )


@deploy("Config")
def apply_config(teardown=False):
    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Aliases",
        src="files/pueue/.pueue_aliases",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.pueue_aliases",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}prun",
        src="files/pueue/prun",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/prun",
        mode=755,
        create_remote_dir=False,
        present=not teardown,
    )

    if teardown:
        files.directory(
            name="Remove",
            path=f"{host.get_fact(server_facts.Home)}/.config/pueue",
            present=False,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        apply_linux(teardown=teardown)
        apply_config(teardown=teardown)


apply()
