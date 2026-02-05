from pathlib import Path

from pyinfra import host, local
from pyinfra.api import exceptions

ALL_TASKS = sorted([d.stem for d in (Path(__file__).parent / "tasks").iterdir() if d.is_dir()])

SKIP_TASKS = {
    "home": {
        "enroot",
        "micromamba",
        "nemo",
    },
    "nvda": {
        "bitwarden",
        "cloudflare",
        "mega",
        "netnewswire",
        "obsidian",
        "pueue",
        "slack",
        "tailscale",
    },
}


def deploy():
    inventory_id = host.data.get("inventory_id")
    if inventory_id not in SKIP_TASKS:
        raise exceptions.DeployError(
            f'Unsupported inventory "{inventory_id}". Pass --data inventory_id=<id> with possible values {list(SKIP_TASKS.keys())}'
        )

    for t in filter(lambda t: t not in SKIP_TASKS[inventory_id], ALL_TASKS):
        local.include(f"tasks/{t}/apply.py")


deploy()
