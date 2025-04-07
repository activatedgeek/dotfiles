from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://github.com/Nukesor/pueue/releases
class Pueue:
    version = "4.0.0"

    class Linux:
        sha256sum = "8be0d92b8766441b4ef9a89a9a817ad76043b00884297c326bc5a585741b23ca"


class Pueued(Pueue):
    class Linux:
        sha256sum = "1a07c82b86115d495fcfa2a1310fc2fe9659b3802b94b7d4ad1f6960d90a5130"


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
            src=f"https://github.com/Nukesor/pueue/releases/download/v{Pueued.version}/pueue-x86_64-unknown-linux-musl",
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/pueue",
            sha256sum=Pueue.Linux.sha256sum,
            mode=755,
        )
        files.download(
            name="pueued",
            src=f"https://github.com/Nukesor/pueue/releases/download/v{Pueued.version}/pueued-x86_64-unknown-linux-musl",
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
