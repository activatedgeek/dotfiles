from pyinfra.api import config

mac = (
    [
        (
            "@local",
            dict(
                backup_dir="~/Cloud\ Drive/Credentials",
                vault_pass=config.INVENTORY_VARS["VAULT_PASS"],
                cloudflare_email=config.INVENTORY_VARS["EMAIL"],
                cloudflare_api_key=config.INVENTORY_VARS["CLOUDFLARE_API_KEY"],
                goatcounter_site=config.INVENTORY_VARS["GOATCOUNTER_SITE"],
                mapbox_access_token=config.INVENTORY_VARS["MAPBOX_ACCESS_TOKEN"],
                discord_webhook_token=config.INVENTORY_VARS["DISCORD_WEBHOOK_TOKEN"],
                hcloud_token=config.INVENTORY_VARS["HCLOUD_TOKEN"],
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
        wandb_api_key=config.INVENTORY_VARS["WANDB_API_KEY"],
        wandb_username=config.INVENTORY_VARS["WANDB_USERNAME"],
        wandb_entity=config.INVENTORY_VARS["WANDB_ENTITY"],
    ),
)
