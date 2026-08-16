import os

from myinfra.inventory import Inventory, InventoryGroup, InventoryHost
from pyinfra.api import config

mac = InventoryGroup(
    name="mac",
    hosts=[
        InventoryHost(
            name="@local",
            vars=dict(
                backup_dir="~/MegaDrive/Credentials",
                cloudflare_email=os.environ["EMAIL"],
                cloudflare_global_api_key=os.environ["CLOUDFLARE_GLOBAL_API_KEY"],
                discord_webhook_token=os.environ.get("DISCORD_WEBHOOK_TOKEN"),
                hcloud_token=os.environ.get("HCLOUD_TOKEN"),
                mapbox_access_token=os.environ.get("MAPBOX_ACCESS_TOKEN"),
                vault_pass=os.environ["VAULT_PASS"],
                wandb_api_key=os.environ.get("WANDB_API_KEY"),
                wandb_username=os.environ.get("WANDB_USERNAME"),
                wandb_entity=os.environ.get("WANDB_ENTITY"),
            ),
        )
    ],
)

inventory = Inventory(
    groups=[mac],
    vars=dict(
        email=os.environ["EMAIL"],
    ),
    binary_versions=config.BINARY_VERSIONS,
)

globals().update(inventory.resolve())
