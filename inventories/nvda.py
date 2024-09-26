import os
from pyinfra.api import config, exceptions

## Ensure SSH keys.
for f in ["files/ssh/nvda/id_ed25519", "files/ssh/nvda/id_ed25519.pub"]:
    if not os.path.isfile(f):
        raise exceptions.InventoryError(f"SSH file {f} not found.")

mac = ([("@local", dict())], dict())

desktop = (
    [
        ("@ssh/nvdesk", dict(store_home="/mnt/${USER}")),
        ("@ssh/nva100", dict(store_home="/mnt/ssd/home/${USER}")),
        # ("@ssh/nvr6000", dict()),
    ],
    dict(),
)

slurm = (
    [
        (
            "@ssh/cs",
            dict(
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_partition="polar,polar2,polar3,polar4,grizzly",
            ),
        ),
        (
            "@ssh/dr",
            dict(
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_partition="batch_block1,batch_block3,batch_block4",
            ),
        ),
        (
            "@ssh/eos",
            dict(
                store_home="/lustre/fsw/llmservice_nemo_robustness/users/${USER}",
                sbatch_partition="batch",
            ),
        ),
    ],
    dict(sbatch_account="llmservice_nemo_robustness", slurm_host=True),
)

linux = (
    [*[h for h, _ in desktop[0]], *[h for h, _ in slurm[0]]],
    dict(
        ssh_key="files/ssh/nvda/id_ed25519",
        ssh_config_file="files/ssh/nvda/config",
        enroot_user=config.INVENTORY_VARS["NVDA_GITLAB_USERNAME"],
        enroot_pass=config.INVENTORY_VARS["NVDA_GITLAB_PAT"],
        google_gemini_api_key=config.INVENTORY_VARS["NVDA_GEMINI_API_KEY"],
        hf_token=config.INVENTORY_VARS["NVDA_HF_TOKEN"],
    ),
)

all = (
    [*[h for h, _ in mac[0]], *linux[0]],
    dict(
        org="nvda",
        email=config.INVENTORY_VARS["NVDA_EMAIL"],
        wandb_api_key=config.INVENTORY_VARS["NVDA_WANDB_API_KEY"],
        wandb_username=config.INVENTORY_VARS["NVDA_WANDB_USERNAME"],
        wandb_entity=config.INVENTORY_VARS["NVDA_WANDB_ENTITY"],
    ),
)
