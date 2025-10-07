from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files, server

from myinfra.facts import brew as brew_facts
from myinfra.facts import docker as docker_facts


@deploy("Config")
def apply_config(teardown=False):
    if teardown:
        remote_home = host.get_fact(server_facts.Home)

        files.directory(
            name="Docker",
            path=f"{remote_home}/.docker",
            present=False,
        )
        files.directory(
            name="Colima",
            path=f"{remote_home}/.colima",
            present=False,
        )
        files.directory(
            name="Colima",
            path=f"{remote_home}/.config/colima",
            present=False,
        )


@deploy("MacOS")
def apply_macos(teardown=False):
    remote_home = host.get_fact(server_facts.Home)
    brew_prefix = host.get_fact(brew_facts.BrewPrefix)

    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["docker"],
        present=not teardown,
    )

    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=[
            "colima",
            "docker-buildx",
            "docker-compose",
            "docker-credential-helper",
        ],
        present=not teardown,
    )

    files.directory(
        name=f"{'Remove ' if teardown else ''}Plugins Dir.",
        path=f"{remote_home}/.docker/cli-plugins",
        mode=755,
        present=not teardown,
    )

    files.link(
        name="compose",
        path=f"{remote_home}/.docker/cli-plugins/docker-compose",
        target=f"{brew_prefix}/opt/docker-compose/bin/docker-compose",
        present=not teardown,
    )

    if not teardown and not host.get_fact(docker_facts.BuildX):
        files.link(
            name="buildx",
            path=f"{remote_home}/.docker/cli-plugins/docker-buildx",
            target=f"{brew_prefix}/bin/docker-buildx",
            present=not teardown,
        )
        server.shell._inner(commands=["docker buildx install"])


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
        apply_config(teardown=teardown)


apply()
