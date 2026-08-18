from pathlib import Path

from dotenv import dotenv_values
from myinfra.inventory import Inventory
from pyinfra.api import config, exceptions

for f in ["tasks/ssh/files/home/id_ed25519", "tasks/ssh/files/home/id_ed25519.pub", "inventories/home.env"]:
    if not Path(f).is_file():
        raise exceptions.InventoryError(f"File {f} not found.")

inventory_env = dotenv_values(Path(__file__).with_suffix(".env"))

inventory = Inventory(
    vars=dict(
        email=inventory_env["EMAIL"],
    ),
    binary_versions=config.BINARY_VERSIONS,
)

inventory.hosts = [
    Inventory.Host(
        name="@local",
        vars=dict(
            backup_dir="~/MegaDrive/Credentials",
            cloudflare_email=inventory_env["EMAIL"],
            cloudflare_global_api_key=inventory_env["CLOUDFLARE_GLOBAL_API_KEY"],
            discord_webhook_token=inventory_env.get("DISCORD_WEBHOOK_TOKEN"),
            hcloud_token=inventory_env.get("HCLOUD_TOKEN"),
            mapbox_access_token=inventory_env.get("MAPBOX_ACCESS_TOKEN"),
            vault_pass=inventory_env["VAULT_PASS"],
            wandb_api_key=inventory_env.get("WANDB_API_KEY"),
            wandb_username=inventory_env.get("WANDB_USERNAME"),
            wandb_entity=inventory_env.get("WANDB_ENTITY"),
        ),
    ),
]

inventory.groups = [Inventory.Group(name="mac", hosts={"@local"})]

globals().update(inventory.resolve())
