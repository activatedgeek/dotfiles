from dataclasses import dataclass
from typing import ClassVar

from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


## https://github.com/Nukesor/pueue/releases
@dataclass
class Pueue(Binary):
    version: ClassVar[str] = "4.0.2"

    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/Nukesor/pueue/releases/download/v{self.version}/pueue-x86_64-unknown-linux-musl",
                "sha256sum": "b94f41f5576b2a4e9c86ec5f0f4df9a68145dd61035113ce25600e21b38f87b7",
            },
            "arm64": {
                "src": f"https://github.com/Nukesor/pueue/releases/download/v{self.version}/pueue-aarch64-unknown-linux-musl",
                "sha256sum": "3a5563377a720a23d4c8c9d6fc3066737de40e6722fab1ec773a61dab92bb970",
            },
        }


@dataclass
class Pueued(Pueue):
    @property
    def _arch_map(self):
        return {
            "amd64": {
                "src": f"https://github.com/Nukesor/pueue/releases/download/v{self.version}/pueued-x86_64-unknown-linux-musl",
                "sha256sum": "7d7f0232c1296aca82881113a8e1f0f75235732a5705854e9f337b3bd961c14a",
            },
            "arm64": {
                "src": f"https://github.com/Nukesor/pueue/releases/download/v{self.version}/pueued-aarch64-unknown-linux-musl",
                "sha256sum": "b5631e6d0c658e9c043ad731317733571d8e26444b70ce10452350344a1f34e2",
            },
        }


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.file(
            name="Uninstall pueue",
            path=f"{remote_home}/.local/bin/pueue",
            present=False,
        )
        files.file(
            name="Uninstall pueued",
            path=f"{remote_home}/.local/bin/pueued",
            present=False,
        )
    else:
        binary = Pueue(arch)
        files.download(
            name="pueue",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/pueue",
            sha256sum=binary.sha256sum,
            mode=755,
        )

        binary = Pueued(arch)
        files.download(
            name="pueued",
            src=binary.src,
            dest=f"{remote_home}/.local/bin/pueued",
            sha256sum=binary.sha256sum,
            mode=755,
        )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Aliases",
        src="tasks/pueue/files/.pueue_aliases",
        dest=f"{remote_home}/.local/profile/.pueue_aliases",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}prun",
        src="tasks/pueue/files/prun",
        dest=f"{remote_home}/.local/bin/prun",
        mode=755,
        create_remote_dir=False,
        present=not teardown,
    )

    if teardown:
        files.directory(
            name="Remove",
            path=f"{remote_home}/.config/pueue",
            present=False,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
        apply_config(teardown=teardown)


apply()
