import os
from pyinfra.api import config, exceptions

## Ensure SSH keys.
for f in ["files/ssh/nyu/id_ed25519", "files/ssh/nyu/id_ed25519.pub"]:
    if not os.path.isfile(f):
        raise exceptions.InventoryError(f"SSH file {f} not found.")

desktop = (
    [
        ("@ssh/gauss", dict()),
        ("@ssh/mint", dict()),
    ],
    dict(store_home="/data/users/${USER}"),
)

hpc = (
    [
        ("@ssh/greene", dict()),
    ],
    dict(store_home="${SCRATCH}"),
)

cims = (
    [
        # ("@ssh/cassio", dict()),
    ],
    dict(),
)

slurm = (
    [*[h for h, _ in hpc[0]], *[h for h, _ in cims[0]]],
    dict(slurm_host=True, docker_username=config.INVENTORY_VARS["DOCKER_USERNAME"]),
)

all = (
    [*[h for h, _ in desktop[0]], *slurm[0]],
    dict(
        org="nyu",
        ssh_key="files/ssh/nyu/id_ed25519",
        ssh_config_file="files/ssh/nyu/config",
        email=config.INVENTORY_VARS["NYU_EMAIL"],
        discord_webhook_token=config.INVENTORY_VARS["DISCORD_WEBHOOK_TOKEN"],
        wandb_username=config.INVENTORY_VARS["WANDB_USERNAME"],
        wandb_entity=config.INVENTORY_VARS["WANDB_ENTITY"],
        wandb_api_key=config.INVENTORY_VARS["WANDB_API_KEY"],
        hf_token=config.INVENTORY_VARS["HF_TOKEN"],
        openai_api_key=config.INVENTORY_VARS["OPENAI_API_KEY"],
        rclone_nyu_drive_client_id=config.INVENTORY_VARS["NYU_DRIVE_CLIENT_ID"],
        rclone_nyu_drive_client_secret=config.INVENTORY_VARS["NYU_DRIVE_CLIENT_SECRET"],
        rclone_nyu_drive_access_token=config.INVENTORY_VARS["NYU_DRIVE_ACCESS_TOKEN"],
        rclone_nyu_drive_refresh_token=config.INVENTORY_VARS["NYU_DRIVE_REFRESH_TOKEN"],
        rclone_nyu_drive_expiry=config.INVENTORY_VARS["NYU_DRIVE_EXPIRY"],
    ),
)
