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
            "desk",
            dict(
                ssh_hostname="aiapps-070225.dyn.nvidia.com",
                store_home="/home/${USER}/store",
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
            "aws-cmh",
            dict(
                ssh_hostname="aws-cmh-slurm-1-dc-01.nvidia.com",
                ssh_aliases=["cmh"],
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=4,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00", overrides=dict(gpus_per_node=4)),
                    gpu_interactive=dict(
                        partition="batch", qos="interactive", time="04:00:00", overrides=dict(gpus_per_node=4)
                    ),
                    cpu=dict(partition="cpu", time="1-00:00:00"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        (
            "aws-dfw",
            dict(
                ssh_hostname="aws-dfw-cs-001-dc-01.nvidia.com",
                ssh_aliases=["adfw"],
                store_home="/scratch/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=4,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00", overrides=dict(gpus_per_node=4)),
                    gpu_interactive=dict(
                        partition="batch", qos="interactive", time="04:00:00", overrides=dict(gpus_per_node=4)
                    ),
                    cpu=dict(partition="cpu", time="1-00:00:00"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw", "/scratch/fsw"],
            ),
        ),
        (
            "aws-iad",
            dict(
                ssh_hostname="aws-iad-cs-002-dc-03.nvidia.com",
                ssh_aliases=["aiad"],
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="pool0", time="04:00:00"),
                    gpu_interactive=dict(partition="interactive", time="09:00:00"),
                    cpu=dict(partition="cpu", time="1-00:00:00"),
                    cpu_interactive=dict(partition="cpu_interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        (
            "dfw",
            dict(
                ssh_hostname="cw-dfw-cs-001-dc-03.cw-dfw-cs-001.hpc.nvidia.com",
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00"),
                    gpu_interactive=dict(partition="interactive", time="04:00:00"),
                    cpu=dict(partition="cpu", time="1-00:00:00"),
                    cpu_interactive=dict(partition="cpu_interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        (
            "eos",
            dict(
                ssh_hostname="login-eos.nvidia.com",
                store_home="/lustre/fsw/nemotron_reason_science/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00", overrides=dict(gpus_per_node=-1)),
                    gpu_interactive=dict(partition="interactive", time="04:00:00", overrides=dict(gpus_per_node=-1)),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        (
            "hsg",
            dict(
                ssh_hostname="oci-hsg-cs-001-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=4,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00", overrides=dict(gpus_per_node=4)),
                    gpu_interactive=dict(
                        partition="batch", qos="interactive", time="04:00:00", overrides=dict(gpus_per_node=4)
                    ),
                    cpu=dict(partition="cpu", time="04:00:00"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-short", time="02:00:00"),
                ),
                enroot_mounts=["/lustre/fsw", "/lustre/fs1"],
            ),
        ),
        (
            "iad",
            dict(
                ssh_hostname="draco-oci-dc-03.draco-oci-iad.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch_block1,batch_block3,batch_block4", time="04:00:00"),
                    gpu_interactive=dict(partition="interactive", time="04:00:00"),
                    cpu=dict(partition="cpu", time="04:00:00"),
                    cpu_interactive=dict(partition="cpu_interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        (
            "nrt",
            dict(
                ssh_hostname="oci-nrt-cs-001-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch_block1", time="04:00:00"),
                    gpu_interactive=dict(partition="interactive", time="04:00:00"),
                    cpu=dict(partition="cpu", time="04:00:00"),
                    cpu_interactive=dict(partition="cpu_interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        (
            "ord",
            dict(
                ssh_hostname="cs-oci-ord-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="polar,polar3,polar4", time="04:00:00"),
                    gpu_interactive=dict(partition="interactive", time="04:00:00"),
                    cpu=dict(partition="cpu", time="04:00:00"),
                    cpu_interactive=dict(partition="cpu_interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        (
            "svg",
            dict(
                ssh_hostname="nsc-svg-slurm-1-dc-02.nvidia.com",
                store_home="/scratch/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_science",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00"),
                    gpu_interactive=dict(partition="batch", qos="interactive", time="04:00:00"),
                    cpu=dict(partition="cpu", time="7-00:00:00"),
                    cpu_interactive=dict(partition="cpu", qos="cpu-interactive", time="1-00:00:00"),
                ),
                enroot_mounts=["/lustre/fsw", "/scratch/fsw"],
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
        dockerhub_username=config.SECRETS.get("DOCKERHUB_USERNAME"),
        dockerhub_password=config.SECRETS.get("DOCKERHUB_PASSWORD"),
        exa_api_key=config.SECRETS.get("EXA_API_KEY"),
        gitlab_token=config.SECRETS.get("GITLAB_TOKEN"),
        hf_token=config.SECRETS.get("HF_TOKEN"),
        ngc_api_key=config.SECRETS.get("NGC_API_KEY"),
        nvinf_api_key=config.SECRETS.get("NVINF_API_KEY"),
        ollama_api_key=config.SECRETS.get("OLLAMA_API_KEY"),
        openai_api_key=config.SECRETS.get("OPENAI_API_KEY"),
        s8k_access_key_id=config.SECRETS.get("S8K_ACCESS_KEY_ID"),
        s8k_secret_access_key=config.SECRETS.get("S8K_SECRET_ACCESS_KEY"),
        tavily_api_key=config.SECRETS.get("TAVILY_API_KEY"),
        wandb_api_key=config.SECRETS.get("WANDB_API_KEY"),
        wandb_username=config.SECRETS.get("WANDB_USERNAME"),
        wandb_entity=config.SECRETS.get("WANDB_ENTITY"),
    ),
)
