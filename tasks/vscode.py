from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.operations import files as myfiles
from myinfra.operations import vscode

_EXTENSIONS = [
    "astro-build.astro-vscode",
    "eamodio.gitlens",
    "ms-azuretools.vscode-docker",
    "ms-python.python",
    "ms-toolsai.jupyter",
    "ms-vscode-remote.remote-ssh",
    "teabyii.ayu",
]


@deploy("MacOS")
def apply_macos(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    brew.casks(
        name=f"{'Uni' if teardown else 'I'}nstall",
        casks=["visual-studio-code"],
        present=not teardown,
    )

    for ext in _EXTENSIONS:
        vscode.extension(
            name=f"{'Remove ' if teardown else ''}Extension {ext}",
            extension=ext,
            present=not teardown,
        )

    for f in ["settings.json", "keybindings.json"]:
        myfiles.copy(
            name=f.capitalize().split(".")[0],
            src=f"files/vscode/{f}",
            dest=f"{remote_home}/Library/Application Support/Code/User/{f}",
            present=not teardown,
            mode=600,
            create_remote_dir=False,
        )


@deploy("MacOS")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    if teardown:
        files.directory(
            name="Remove .vscode-server",
            path=f"{remote_home}/.vscode-server",
            present=False,
        )

        files.directory(
            name="Remove .vscode",
            path=f"{remote_home}/.vscode",
            present=False,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)

    apply_config(teardown=teardown)


apply()
