from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/Nukesor/pueue/releases
@dataclass
class Pueue(Binary):
    version: ClassVar[str] = "4.0.1"

    @property
    def _arch_map(self):
        return {
            "x86_64": {
                "src": f"https://github.com/Nukesor/pueue/releases/download/v{self.version}/pueue-x86_64-unknown-linux-musl",
                "sha256sum": "16aea6654b3915c6495bb2f456184fd7f3d418de3f74afb5eab04ae953cdfedf",
            }
        }


@dataclass
class Pueued(Pueue):
    @property
    def _arch_map(self):
        return {
            "x86_64": {
                "src": f"https://github.com/Nukesor/pueue/releases/download/v{self.version}/pueued-x86_64-unknown-linux-musl",
                "sha256sum": "8a97b176f55929e37cda49577b28b66ea345151adf766b9d8efa8c9d81525a0b",
            }
        }


@deploy("Linux")
def apply_linux(arch, teardown=False):
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
        binary = Pueue(arch)
        files.download(
            name="pueue",
            src=binary.src,
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/pueue",
            sha256sum=binary.sha256sum,
            mode=755,
        )

        binary = Pueued(arch)
        files.download(
            name="pueued",
            src=binary.src,
            dest=f"{host.get_fact(server_facts.Home)}/.local/bin/pueued",
            sha256sum=binary.sha256sum,
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
        arch = host.get_fact(server_facts.Arch)
        apply_linux(arch, teardown=teardown)
        apply_config(teardown=teardown)


apply()
