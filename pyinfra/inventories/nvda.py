import os

from pyinfra.api import config, exceptions

## Ensure SSH keys.
for f in ["tasks/ssh/files/nvda/id_ed25519", "tasks/ssh/files/nvda/id_ed25519.pub"]:
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
                ssh_hostname="aiapps-110221.dyn.nvidia.com",
                store_home="/mnt/ssd/home/${USER}",
                skip=True,
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
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
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
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partition="batch",
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
                skip=True,
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
                skip=True,
            ),
        ),
        (
            "@ssh/ord",
            dict(
                ssh_hostname="cs-oci-ord-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partition="polar,polar3,polar4",
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
    ),
)

all = (
    [*[h for h, _ in mac[0]], *linux[0]],
    dict(
        email=config.INVENTORY_VARS["NVIDIA_EMAIL"],
        ssh_user=config.INVENTORY_VARS["NVIDIA_EMAIL"].split("@")[0],
        ssh_key="tasks/ssh/files/nvda/id_ed25519",
        ssh_config_file="/dev/null",
        skip_tasks={
            "bitwarden",
            "brave",
            "cloudflare",
            "mega",
            "netnewswire",
            "obsidian",
            "slack",
            "tailscale",
        },
        ## Secrets.
        azure_openai_api_key=config.INVENTORY_VARS.get("AZURE_OPENAI_API_KEY"),
        brave_api_key=config.INVENTORY_VARS.get("BRAVE_API_KEY"),
        dagshub_username=config.INVENTORY_VARS.get("DAGSHUB_USERNAME"),
        dagshub_user_token=config.INVENTORY_VARS.get("DAGSHUB_USER_TOKEN"),
        discord_webhook_token=config.INVENTORY_VARS.get("DISCORD_WEBHOOK_TOKEN"),
        docker_hub_username=config.INVENTORY_VARS.get("DOCKER_HUB_USERNAME"),
        docker_hub_password=config.INVENTORY_VARS.get("DOCKER_HUB_PASSWORD"),
        exa_api_key=config.INVENTORY_VARS.get("EXA_API_KEY"),
        gitlab_token=config.INVENTORY_VARS.get("GITLAB_TOKEN"),
        hf_token=config.INVENTORY_VARS.get("HF_TOKEN"),
        ngc_api_key=config.INVENTORY_VARS.get("NGC_API_KEY"),
        nvinf_api_key=config.INVENTORY_VARS.get("NVINF_API_KEY"),
        openai_api_key=config.INVENTORY_VARS.get("OPENAI_API_KEY"),
        tavily_api_key=config.INVENTORY_VARS.get("TAVILY_API_KEY"),
        wandb_api_key=config.INVENTORY_VARS.get("WANDB_API_KEY"),
        wandb_username=config.INVENTORY_VARS.get("WANDB_USERNAME"),
        wandb_entity=config.INVENTORY_VARS.get("WANDB_ENTITY"),
    ),
)
