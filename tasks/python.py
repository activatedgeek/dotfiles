from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files


@deploy("MacOS")
def apply_macos(teardown=False):
    # brew.packages(
    #     name=f"{'Uni' if teardown else 'I'}nstall",
    #     packages=["python"],
    #     present=not teardown,
    # )
    ...


@deploy("Config")
def apply_config(teardown=False):
    if teardown:
        files.file(
            name="Remove History",
            path=f"{host.get_fact(server_facts.Home)}/.python_history",
            present=False,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)

    apply_config(teardown=teardown)


apply()
