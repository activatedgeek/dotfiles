from dataclasses import dataclass, field
from typing import ClassVar

from pyinfra import host, local
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.facts import server as myserver_facts
from myinfra.operations import files as myfiles
from myinfra.utils import Binary


@dataclass
class Oxen(Binary):
    gh_repo: ClassVar[str] = "Oxen-AI/Oxen"
    version: ClassVar[str] = "v0.45.0"
    asset_map: ClassVar[dict[str, dict[str, str]]] = field(
        default_factory=lambda: {
            "amd64": {
                "name": "oxen-linux-x86_64.tar.gz",
                "sha256sum": "7ba46b091c118a7567f9ad19a6eacfecfa4dc2513785a0e82078a4970947da13",
            },
            "arm64": {
                "name": "oxen-linux-arm64.tar.gz",
                "sha256sum": "c53c9eac091ae96b3c3b076aec004e20d0d769c87dd01dde09e3c70c29647fd4",
            },
        }
    )


@deploy("Linux")
def apply_linux(arch, teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    binary = Oxen(arch)
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=binary.src,
        dest=f"{remote_home}/.local/bin/oxen",
        sha256sum=binary.sha256sum,
        mode=755,
        present=not teardown,
    )


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["oxen"],
        present=not teardown,
    )


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name="Config Dir.",
        path=f"{remote_home}/.config/oxen",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}user_config.toml",
        src="tasks/oxen/templates/user_config.toml.j2",
        dest=f"{remote_home}/.config/oxen/user_config.toml",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        oxen_name=local.shell("id -F"),
        oxen_email=host.data.email,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}auth_config.toml",
        src="tasks/oxen/templates/auth_config.toml.j2",
        dest=f"{remote_home}/.config/oxen/auth_config.toml",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        oxen_auth_token=host.data.get("oxen_auth_token"),
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        arch = host.get_fact(myserver_facts.DpkgArch)
        apply_linux(arch, teardown=teardown)

    apply_config(teardown=teardown)


apply()
