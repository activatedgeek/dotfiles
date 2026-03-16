from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

from pyinfra import host


@deploy("WandB")
def apply():
    if not all([host.data.get(k, "") for k in ["wandb_username", "wandb_api_key", "wandb_entity"]]):
        return

    teardown = host.data.get("teardown", False)

    if teardown:
        files.directory(
            name="Remove Config",
            path=f"{host.get_fact(server_facts.Home)}/.config/wandb",
            present=False,
        )
