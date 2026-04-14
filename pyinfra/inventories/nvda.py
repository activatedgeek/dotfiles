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
                skip_host=True,
            ),
        ),
    ],
    dict(),
)

##
# For partition info, run
#   ```shell
#   scontrol show partitions | grep -E "PartitionName|AllowQos|QoS"
#   ```
# For qos info, run
#   ```shell
#   sacctmgr show qos format=Name%16,MaxWall,MinTRES,MaxTRES,MaxJobsPU,MaxSubmitPU,MaxTRESPU
#   ```
slurm = (
    [
        (
            "@ssh/adfw",
            dict(
                ssh_hostname="aws-dfw-cs-001-dc-01.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="batch", qos="interactive"),
                    cpu=dict(partition="cpu", qos="cpu-short"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-interactive"),
                ),
                sbatch_params=dict(
                    gpus_per_node=4,
                ),
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/aiad",
            dict(
                ssh_hostname="aws-iad-cs-002-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_partitions=dict(
                    gpu=dict(partition="pool0"),
                    gpu_interactive=dict(partition="interactive"),
                    cpu=dict(partition="cpu_short"),
                    cpu_interactive=dict(partition="cpu_interactive"),
                ),
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/dfw",
            dict(
                ssh_hostname="cw-dfw-cs-001-dc-03.cw-dfw-cs-001.hpc.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="interactive"),
                    cpu=dict(partition="cpu_short"),
                    cpu_interactive=dict(partition="cpu_interactive"),
                ),
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
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="interactive"),
                    cpu=dict(partition="batch"),
                    cpu_interactive=dict(partition="interactive"),
                ),
                sbatch_params=dict(
                    gpus_per_node=-1,
                ),
                enroot_mounts=[
                    "/lustre/fsw/llmservice_nemo_reasoning",
                ],
            ),
        ),
        (
            "@ssh/hel",
            dict(
                ssh_hostname="nb-hel-cs-001-dc-02.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="interactive"),
                    cpu=dict(partition="cpu_short"),
                    cpu_interactive=dict(partition="cpu_interactive"),
                ),
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/gnrt",
            dict(
                ssh_hostname="gcp-nrt-cs-001-dc-001.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="batch", qos="interactive"),
                    cpu=dict(partition="cpu"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-short"),
                ),
                sbatch_params=dict(
                    gpus_per_node=4,
                ),
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/hsg",
            dict(
                ssh_hostname="oci-hsg-cs-001-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="batch", qos="interactive"),
                    cpu=dict(partition="cpu", qos="cpu-short"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-short"),
                ),
                sbatch_params=dict(
                    gpus_per_node=4,
                ),
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
                sbatch_partitions=dict(
                    gpu=dict(partition="batch_block1,batch_block3,batch_block4"),
                    gpu_interactive=dict(partition="interactive"),
                    cpu=dict(partition="cpu_short"),
                    cpu_interactive=dict(partition="cpu_interactive"),
                ),
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/nsvg",
            dict(
                ssh_hostname="nsc-svg-slurm-1-login-02.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="batch", qos="interactive"),
                    cpu=dict(partition="cpu", qos="cpu-short"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-interactive"),
                ),
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/ord",
            dict(
                ssh_hostname="cs-oci-ord-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="llmservice_nemo_reasoning",
                sbatch_partitions=dict(
                    gpu=dict(partition="polar,polar3,polar4"),
                    gpu_interactive=dict(partition="interactive"),
                    cpu=dict(partition="cpu_short"),
                    cpu_interactive=dict(partition="cpu_interactive"),
                ),
                enroot_mounts=[
                    "/lustre/fsw/portfolios/llmservice",
                ],
            ),
        ),
        (
            "@ssh/pdx",
            dict(
                ssh_hostname="cw-pdx-cs-001-dc-02.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_partitions=dict(
                    gpu=dict(partition="batch"),
                    gpu_interactive=dict(partition="interactive"),
                    cpu=dict(partition="cpu_short"),
                    cpu_interactive=dict(partition="cpu_interactive"),
                ),
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
        email=config.SECRETS["NVIDIA_EMAIL"],
        ssh_user=config.SECRETS["NVIDIA_EMAIL"].split("@")[0],
        ssh_key="tasks/ssh/files/nvda/id_ed25519",
        ssh_config_file="/dev/null",
        skip_tasks={
            "bitwarden",
            "cloudflare",
            "mega",
            "netnewswire",
            "obsidian",
            "tailscale",
        },
        ## Latest binary versions
        binary_versions=config.BINARY_VERSIONS,
        ## Secrets.
        azure_openai_api_key=config.SECRETS.get("AZURE_OPENAI_API_KEY"),
        brave_api_key=config.SECRETS.get("BRAVE_API_KEY"),
        dagshub_username=config.SECRETS.get("DAGSHUB_USERNAME"),
        dagshub_user_token=config.SECRETS.get("DAGSHUB_USER_TOKEN"),
        discord_webhook_token=config.SECRETS.get("DISCORD_WEBHOOK_TOKEN"),
        docker_hub_username=config.SECRETS.get("DOCKER_HUB_USERNAME"),
        docker_hub_password=config.SECRETS.get("DOCKER_HUB_PASSWORD"),
        exa_api_key=config.SECRETS.get("EXA_API_KEY"),
        gitlab_token=config.SECRETS.get("GITLAB_TOKEN"),
        hf_token=config.SECRETS.get("HF_TOKEN"),
        ngc_api_key=config.SECRETS.get("NGC_API_KEY"),
        nvinf_api_key=config.SECRETS.get("NVINF_API_KEY"),
        ollama_api_key=config.SECRETS.get("OLLAMA_API_KEY"),
        openai_api_key=config.SECRETS.get("OPENAI_API_KEY"),
        tavily_api_key=config.SECRETS.get("TAVILY_API_KEY"),
        wandb_api_key=config.SECRETS.get("WANDB_API_KEY"),
        wandb_username=config.SECRETS.get("WANDB_USERNAME"),
        wandb_entity=config.SECRETS.get("WANDB_ENTITY"),
    ),
)
