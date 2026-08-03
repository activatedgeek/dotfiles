import os

from pyinfra.api import config

mac = (
    [
        (
            "@local",
            dict(
                backup_dir="~/Cloud\ Drive/Credentials",
                cloudflare_email=os.environ["EMAIL"],
                cloudflare_api_key=os.environ["CLOUDFLARE_API_KEY"],
                discord_webhook_token=os.environ.get("DISCORD_WEBHOOK_TOKEN"),
                goatcounter_site=os.environ.get("GOATCOUNTER_SITE"),
                hcloud_token=os.environ.get("HCLOUD_TOKEN"),
                mapbox_access_token=os.environ.get("MAPBOX_ACCESS_TOKEN"),
                vault_pass=os.environ["VAULT_PASS"],
                wandb_api_key=os.environ.get("WANDB_API_KEY"),
                wandb_username=os.environ.get("WANDB_USERNAME"),
                wandb_entity=os.environ.get("WANDB_ENTITY"),
            ),
        )
    ],
    dict(),
)

all = (
    [h for h, _ in mac[0]],
    dict(
        email=os.environ["EMAIL"],
        skip_tasks={},
        ## Latest binary versions
        binary_versions=config.BINARY_VERSIONS,
    ),
)
