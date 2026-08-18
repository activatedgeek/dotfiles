import os

from myinfra.inventory import Inventory, InventoryGroup, InventoryHost
from pyinfra.api import config, exceptions

## Ensure SSH keys.
for f in ["tasks/ssh/files/nvda/id_ed25519", "tasks/ssh/files/nvda/id_ed25519.pub"]:
    if not os.path.isfile(f):
        raise exceptions.InventoryError(f"SSH file {f} not found.")

mac = InventoryGroup(
    name="mac",
    hosts=[InventoryHost(name="@local")],
)

desktop = InventoryGroup(
    name="desktop",
    hosts=[
        InventoryHost(
            name="desk",
            vars=dict(
                ssh_hostname="aiapps-070225.dyn.nvidia.com",
                store_home="/home/${USER}/store",
            ),
        ),
    ],
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
slurm = InventoryGroup(
    name="slurm",
    hosts=[
        InventoryHost(
            name="aws-cmh",
            vars=dict(
                ssh_hostname="aws-cmh-slurm-1-dc-01.nvidia.com",
                ssh_code_hostname="aws-cmh-slurm-1-vscode-02.nvidia.com",
                ssh_aliases=["cmh"],
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
                ## NOTE: Shares fs with aws-cmh-2.
                # skip_host=True,
            ),
        ),
        InventoryHost(
            name="aws-cmh-2",
            vars=dict(
                ssh_hostname="aws-cmh-slurm-2-dc-03.nvidia.com",
                ssh_code_hostname="aws-cmh-slurm-2-vscode-02.nvidia.com",
                ssh_aliases=["cmh2"],
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
                ## NOTE: Shares fs with aws-cmh.
                skip_host=True,
            ),
        ),
        InventoryHost(
            name="aws-dfw",
            vars=dict(
                ssh_hostname="aws-dfw-cs-001-dc-01.nvidia.com",
                ssh_aliases=["adfw"],
                store_home="/scratch/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
        InventoryHost(
            name="aws-iad",
            vars=dict(
                ssh_hostname="aws-iad-cs-002-dc-03.nvidia.com",
                ssh_aliases=["aiad"],
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
        InventoryHost(
            name="dfw",
            vars=dict(
                ssh_hostname="cw-dfw-cs-001-dc-03.cw-dfw-cs-001.hpc.nvidia.com",
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00"),
                    gpu_interactive=dict(partition="interactive", time="04:00:00"),
                    cpu=dict(partition="cpu", time="04:00:00"),
                    cpu_interactive=dict(partition="cpu_interactive", time="04:00:00"),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        InventoryHost(
            name="eos",
            vars=dict(
                ssh_hostname="login-eos.nvidia.com",
                store_home="/lustre/fsw/nemotron_reason_science/users/${USER}",
                sbatch_account="nemotron_reason_math",
                sbatch_gpus_per_node=8,
                sbatch_partitions=dict(
                    gpu=dict(partition="batch", time="04:00:00", overrides=dict(gpus_per_node=-1)),
                    gpu_interactive=dict(partition="interactive", time="04:00:00", overrides=dict(gpus_per_node=-1)),
                ),
                enroot_mounts=["/lustre/fsw"],
            ),
        ),
        InventoryHost(
            name="hsg",
            vars=dict(
                ssh_hostname="oci-hsg-cs-001-dc-03.nvidia.com",
                ssh_code_hostname="oci-hsg-cs-001-vscode-02.nvidia.com",
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
        InventoryHost(
            name="iad",
            vars=dict(
                ssh_hostname="draco-oci-dc-03.draco-oci-iad.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
        InventoryHost(
            name="nrt",
            vars=dict(
                ssh_hostname="oci-nrt-cs-001-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
        InventoryHost(
            name="ord",
            vars=dict(
                ssh_hostname="cs-oci-ord-dc-03.nvidia.com",
                store_home="/lustre/fsw/portfolios/llmservice/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
        InventoryHost(
            name="svg",
            vars=dict(
                ssh_hostname="nsc-svg-slurm-1-dc-02.nvidia.com",
                store_home="/scratch/fsw/portfolios/nemotron/users/${USER}",
                sbatch_account="nemotron_reason_math",
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
)

linux = InventoryGroup(
    name="linux",
    hosts=[*desktop.hosts, *slurm.hosts],
    vars=dict(
        term="xterm-256color",
        ## Secrets.
        ngc_api_key=os.environ.get("NGC_API_KEY"),
        nvinf_api_key=os.environ.get("NVINF_API_KEY"),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        hf_token=os.environ.get("HF_TOKEN"),
        wandb_api_key=os.environ.get("WANDB_API_KEY"),
        wandb_username=os.environ.get("WANDB_USERNAME"),
        wandb_entity=os.environ.get("WANDB_ENTITY"),
    ),
)

inventory = Inventory(
    groups=[mac, desktop, slurm, linux],
    vars=dict(
        email=os.environ["NVIDIA_EMAIL"],
        ssh_user=os.environ["NVIDIA_EMAIL"].split("@")[0],
        ssh_key="tasks/ssh/files/nvda/id_ed25519",
        ssh_config_file="/dev/null",
        ## Secrets.
        dagshub_username=os.environ.get("DAGSHUB_USERNAME"),
        dagshub_user_token=os.environ.get("DAGSHUB_USER_TOKEN"),
        discord_webhook_token=os.environ.get("DISCORD_WEBHOOK_TOKEN"),
        dockerhub_username=os.environ.get("DOCKERHUB_USERNAME"),
        dockerhub_password=os.environ.get("DOCKERHUB_PASSWORD"),
        gitlab_token=os.environ.get("GITLAB_TOKEN"),
        s8k_access_key_id=os.environ.get("S8K_ACCESS_KEY_ID"),
        s8k_secret_access_key=os.environ.get("S8K_SECRET_ACCESS_KEY"),
    ),
    binary_versions=config.BINARY_VERSIONS,
    skip_tasks={
        "bitwarden",
        "cloudflare",
        "codex",
        "mega",
        "netnewswire",
        "obsidian",
        "tailscale",
    },
)

globals().update(inventory.resolve())
