from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.tap(
        name=f"{'Remove' if teardown else 'Add'} tap",
        src="tw93/tap/mole",
        present=not teardown,
    )

    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["mole"],
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)


apply()
