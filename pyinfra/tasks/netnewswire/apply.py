from myinfra.facts import mac as mac_facts
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew

from pyinfra import host


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["netnewswire"],
        present=not teardown,
    )


@deploy("NetNewsWire")
def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)


def pre_check():
    return not host.get_fact(mac_facts.MacOSVM)
