from dataclasses import dataclass
from typing import ClassVar

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files, python

from pyinfra import host


@dataclass
class Pueue(Binary):
    gh_repo: ClassVar[str] = "Nukesor/pueue"
    version: ClassVar[str] = "v4.0.4"

    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "pueue-x86_64-unknown-linux-musl",
                "sha256sum": "c1b10d7e4e62211075ddd0e1dc3e8cbfc5a43d662cb3be7402a28504e23fcb51",
            },
            "arm64": {
                "name": "pueue-aarch64-unknown-linux-musl",
                "sha256sum": "759bf5100a51024997111c6913aaf3330a0cdfd893ff552dcf429ae9b5e01e09",
            },
        }


@dataclass
class Pueued(Pueue):
    @property
    def asset_map(self):
        return {
            "amd64": {
                "name": "pueued-x86_64-unknown-linux-musl",
                "sha256sum": "5afeff6adbafb909e8d54e2caff158e6966c2adffa2c09e60fd631cc51b60390",
            },
            "arm64": {
                "name": "pueued-aarch64-unknown-linux-musl",
                "sha256sum": "332c5ef74270b64aeaf04894c8c04826f3422eb7d50dbd1a8e0706d74a42f653",
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

        python.call(
            name="Check Latest",
            function=binary.is_latest,
            _run_once=True,
        )

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


@deploy("Pueue")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)
        apply_config(teardown=teardown)
