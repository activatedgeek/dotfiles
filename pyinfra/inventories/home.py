from pyinfra.api import config

mac = (
    [
        (
            "@local",
            dict(
                backup_dir="~/Cloud\ Drive/Credentials",
                cloudflare_email=config.SECRETS["EMAIL"],
                cloudflare_api_key=config.SECRETS["CLOUDFLARE_API_KEY"],
                discord_webhook_token=config.SECRETS.get("DISCORD_WEBHOOK_TOKEN"),
                goatcounter_site=config.SECRETS.get("GOATCOUNTER_SITE"),
                hcloud_token=config.SECRETS.get("HCLOUD_TOKEN"),
                mapbox_access_token=config.SECRETS.get("MAPBOX_ACCESS_TOKEN"),
                ollama_api_key=config.SECRETS.get("OLLAMA_API_KEY"),
                vault_pass=config.SECRETS["VAULT_PASS"],
                wandb_api_key=config.SECRETS.get("WANDB_API_KEY"),
                wandb_username=config.SECRETS.get("WANDB_USERNAME"),
                wandb_entity=config.SECRETS.get("WANDB_ENTITY"),
            ),
        )
    ],
    dict(),
)

all = (
    [h for h, _ in mac[0]],
    dict(
        email=config.SECRETS["EMAIL"],
        skip_tasks={
            "enroot",
            "nemo",
        },
        ## Latest binary versions
        binary_versions=config.BINARY_VERSIONS,
    ),
)
