from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew
from pyinfra.facts import server as server_facts


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.tap(
        name="Untap" if teardown else "Tap",
        src="localsend/localsend",
        present=not teardown,
    )

    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["localsend"],
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)


apply()
