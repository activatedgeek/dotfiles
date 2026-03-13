from pyinfra.api import config

mac = (
    [
        (
            "@local",
            dict(
                backup_dir="~/Cloud\ Drive/Credentials",
                cloudflare_email=config.INVENTORY_VARS["EMAIL"],
                cloudflare_api_key=config.INVENTORY_VARS["CLOUDFLARE_API_KEY"],
                discord_webhook_token=config.INVENTORY_VARS.get("DISCORD_WEBHOOK_TOKEN"),
                goatcounter_site=config.INVENTORY_VARS.get("GOATCOUNTER_SITE"),
                hcloud_token=config.INVENTORY_VARS.get("HCLOUD_TOKEN"),
                mapbox_access_token=config.INVENTORY_VARS.get("MAPBOX_ACCESS_TOKEN"),
                vault_pass=config.INVENTORY_VARS["VAULT_PASS"],
                wandb_api_key=config.INVENTORY_VARS.get("WANDB_API_KEY"),
                wandb_username=config.INVENTORY_VARS.get("WANDB_USERNAME"),
                wandb_entity=config.INVENTORY_VARS.get("WANDB_ENTITY"),
            ),
        )
    ],
    dict(),
)

all = (
    [h for h, _ in mac[0]],
    dict(
        org="home",
        email=config.INVENTORY_VARS["EMAIL"],
    ),
)
