from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import brew, files
from pyinfra.facts import server as server_facts

from myinfra.operations import vscode, files as myfiles


_EXTENSIONS = [
    "astro-build.astro-vscode",
    "eamodio.gitlens",
    "james-yu.latex-workshop",
    "ms-azuretools.vscode-docker",
    "ms-python.python",
    "ms-toolsai.jupyter",
    "ms-vscode-remote.remote-ssh",
    "teabyii.ayu",
]


@deploy("MacOS")
def apply_macos(teardown=False):
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
            dest=f"{host.get_fact(server_facts.Home)}/Library/Application Support/Code/User/{f}",
            present=not teardown,
            mode=600,
            create_remote_dir=False,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)

    if teardown:
        files.directory(
            name="Remove .vscode-server",
            path=f"{host.get_fact(server_facts.Home)}/.vscode-server",
            present=False,
        )

        files.directory(
            name="Remove .vscode",
            path=f"{host.get_fact(server_facts.Home)}/.vscode",
            present=False,
        )


apply()
