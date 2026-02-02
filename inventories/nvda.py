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
                store_home="/mnt/ssd/home/${USER}",
            ),
        ),
    ],
    dict(),
)

slurm = (
    [
        (
            "@ssh/dfw",
            dict(
                ssh_hostname="cw-dfw-cs-001-dc-03.cw-dfw-cs-001.hpc.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partition="batch",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/eos",
            dict(
                ssh_hostname="login-eos02.eos.clusters.nvidia.com",
                store_home="/lustre/fsw/llmservice_nemo_robustness/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partition="batch",
                nemo_skills_disable_gpus_per_node=True,
                nemo_skills_disable_cpu_partition=True,
                enroot_mounts=[
                    "/lustre/fsw/llmservice_nemo_reasoning",
                ],
            ),
        ),
        (
            "@ssh/hsg",
            dict(
                ssh_hostname="oci-hsg-cs-001-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partition="batch",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/iad",
            dict(
                ssh_hostname="draco-oci-dc-03.draco-oci-iad.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/projects/llmservice_nemo_robustness/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partition="batch_block1,batch_block3,batch_block4",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/lax",
            dict(
                ssh_port=30022,
                ssh_hostname="lbd-lax-cs-001-login-01.nvidia.com",
                store_home="/scratch/fsw/portfolios/llmservice/projects/llmservice_nemo_robustness/users/${USER}",
                sbatch_account="llmservice_nemo_robustness",
                sbatch_partition="batch",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/nrt",
            dict(
                ssh_hostname="oci-nrt-cs-001-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemotron_nano",
                sbatch_partition="batch_block1",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/ord",
            dict(
                ssh_hostname="cs-oci-ord-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/projects/llmservice_nemo_robustness/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partition="polar,polar3,polar4,grizzly",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
    ],
    dict(),
)

linux = (
    [*[h for h, _ in desktop[0]], *[h for h, _ in slurm[0]]],
    dict(
        term="xterm-256color",
        bbh_nvidia_api_key=config.INVENTORY_VARS["BBH_NVIDIA_API_KEY"],
        discord_webhook_token=config.INVENTORY_VARS["DISCORD_WEBHOOK_TOKEN"],
        nvidia_api_key=config.INVENTORY_VARS["NVIDIA_API_KEY"],
        exa_api_key=config.INVENTORY_VARS["EXA_API_KEY"],
        tavily_api_key=config.INVENTORY_VARS["TAVILY_API_KEY"],
        brave_api_key=config.INVENTORY_VARS["BRAVE_API_KEY"],
        google_search_engine_id=config.INVENTORY_VARS["GOOGLE_SEARCH_ENGINE_ID"],
        google_search_api_key=config.INVENTORY_VARS["GOOGLE_SEARCH_API_KEY"],
        hf_token=config.INVENTORY_VARS["HF_TOKEN"],
        gitlab_token=config.INVENTORY_VARS["GITLAB_TOKEN"],
        wandb_api_key=config.INVENTORY_VARS["WANDB_API_KEY"],
        wandb_username=config.INVENTORY_VARS["WANDB_USERNAME"],
        wandb_entity=config.INVENTORY_VARS["WANDB_ENTITY"],
        docker_hub_username=config.INVENTORY_VARS["DOCKER_HUB_USERNAME"],
        docker_hub_password=config.INVENTORY_VARS["DOCKER_HUB_PASSWORD"],
        openai_client_id=config.INVENTORY_VARS["OPENAI_CLIENT_ID"],
        openai_client_secret=config.INVENTORY_VARS["OPENAI_CLIENT_SECRET"],
        azure_openai_api_key=config.INVENTORY_VARS["AZURE_OPENAI_API_KEY"],
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
