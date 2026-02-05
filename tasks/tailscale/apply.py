from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import apt, brew


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["tailscale-app"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    if not teardown:
        ## FIXME:
        apt.key(
            name="Add GPG Key",
            src="https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg",
        )

    apt.repo(
        name=f"{'Remove' if teardown else 'Add'} repo",
        src="deb [signed-by=/usr/share/keyrings/tailscale-archive-keyring.gpg] https://pkgs.tailscale.com/stable/ubuntu noble main",
        filename="tailscale",
        present=not teardown,
    )

    if not teardown:
        apt.update(name="apt update")

    apt.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["tailscale"],
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    # elif kernel == "Linux":
    #     apply_linux(teardown=teardown)


apply()
