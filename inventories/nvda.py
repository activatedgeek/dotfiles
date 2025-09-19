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
                store_home="/home/${USER}/store",
            ),
        ),
        (
            "@ssh/bigdesk",
            dict(
                ssh_hostname="10.110.40.240",
                store_home="/mnt/ssd/home/${USER}/store",
            ),
        ),
    ],
    dict(),
)

slurm = (
    [
        (
            "@ssh/cs",
            dict(
                ssh_hostname="cs-oci-ord-dc-02.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/projects/llmservice_nemo_robustness/users/${USER}/store",
                sbatch_partition="polar,polar3,polar4,grizzly",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice/users/igitman/hf_models",
                ],
            ),
        ),
        (
            "@ssh/dfw",
            dict(
                ssh_hostname="cw-dfw-cs-001-dc-02.cw-dfw-cs-001.hpc.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}/store",
                sbatch_partition="batch",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice/users/igitman/hf_models",
                ],
            ),
        ),
        (
            "@ssh/dr",
            dict(
                ssh_hostname="draco-oci-dc-02.draco-oci-iad.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/projects/llmservice_nemo_robustness/users/${USER}/store",
                sbatch_partition="batch_block1,batch_block3,batch_block4",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice/users/igitman/llm/hf_models",
                    "/lustre/fsw/portfolios/llmservice/users/sdiao/wiki-202503-index",
                    "/lustre/fsw/portfolios/llmservice/users/ebakhturina/data/stem_v2_seed_data",
                ],
            ),
        ),
        (
            "@ssh/eos",
            dict(
                ssh_hostname="login-eos02.eos.clusters.nvidia.com",
                store_home="/lustre/fsw/llmservice_nemo_robustness/users/${USER}/store",
                sbatch_partition="batch",
                nemo_skills_disable_gpus_per_node=True,
            ),
        ),
    ],
    dict(
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
        exa_api_key=config.INVENTORY_VARS["EXA_API_KEY"],
        hf_token=config.INVENTORY_VARS["HF_TOKEN"],
        gitlab_token=config.INVENTORY_VARS["GITLAB_TOKEN"],
        wandb_api_key=config.INVENTORY_VARS["WANDB_API_KEY"],
        wandb_username=config.INVENTORY_VARS["WANDB_USERNAME"],
        wandb_entity=config.INVENTORY_VARS["WANDB_ENTITY"],
        git_gpgsign=True,
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
