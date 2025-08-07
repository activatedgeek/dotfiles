import os
from pyinfra.api import config, exceptions

## Ensure SSH keys.
for f in ["files/ssh/nvda/id_ed25519", "files/ssh/nvda/id_ed25519.pub"]:
    if not os.path.isfile(f):
        raise exceptions.InventoryError(f"SSH file {f} not found.")

mac = ([("@local", dict())], dict())

desktop = (
    [
        (
            "@ssh/desk",
            dict(
                ssh_hostname="aiapps-070225.dyn.nvidia.com",
                store_home="${HOME}/store",
            ),
        )
    ],
    dict(),
)

slurm = (
    [
        (
            "@ssh/cs",
            dict(
                ssh_hostname="cs-oci-ord-dc-02.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_partition="polar",
            ),
        ),
        (
            "@ssh/dfw",
            dict(
                ssh_hostname="cw-dfw-cs-001-dc-02.cw-dfw-cs-001.hpc.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_partition="batch,batch_short",
            ),
        ),
        (
            "@ssh/dr",
            dict(
                ssh_hostname="draco-oci-dc-02.draco-oci-iad.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_partition="batch_block1,batch_block2,batch_block3,batch_block4",
            ),
        ),
        (
            "@ssh/eos",
            dict(
                ssh_hostname="login-eos02.eos.clusters.nvidia.com",
                store_home="/lustre/fsw/llmservice_nemo_robustness/users/${USER}",
                sbatch_partition="batch",
            ),
        ),
    ],
    dict(
        slurm_host=True,
        sbatch_account="llmservice_nemo_robustness",
        sbatch_overcommit=True,
    ),
)

linux = (
    [*[h for h, _ in desktop[0]], *[h for h, _ in slurm[0]]],
    dict(
        term="xterm-256color",
        discord_webhook_token=config.INVENTORY_VARS["DISCORD_WEBHOOK_TOKEN"],
        nvidia_api_key=config.INVENTORY_VARS["NVIDIA_API_KEY"],
        hf_token=config.INVENTORY_VARS["HF_TOKEN"],
        gitlab_token=config.INVENTORY_VARS["GITLAB_TOKEN"],
        wandb_api_key=config.INVENTORY_VARS["WANDB_API_KEY"],
        wandb_username=config.INVENTORY_VARS["WANDB_USERNAME"],
        wandb_entity=config.INVENTORY_VARS["WANDB_ENTITY"],
    ),
)

all = (
    [*[h for h, _ in mac[0]], *linux[0]],
    dict(
        org="nvda",
        ssh_user=config.INVENTORY_VARS["NVIDIA_EMAIL"].split("@")[0],
        ssh_key="files/ssh/nvda/id_ed25519",
        ssh_config_file="/dev/null",
        email=config.INVENTORY_VARS["NVIDIA_EMAIL"],
    ),
)
