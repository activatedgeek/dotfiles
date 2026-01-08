from pyinfra import local


def deploy_tasks():
    for task in [
        "bash",
        "bottom",
        "brave",
        "discord",
        "enroot",
        "ghostty",
        "git",
        "jq",
        "micro",
        "micromamba",
        "mole",
        "nemo",
        "python",
        "rclone",
        "slurm",
        "ssh",
        "starship",
        "stirling-pdf",
        "tmux",
        "uv",
        "wandb",
        "zed",
    ]:
        local.include(f"tasks/{task}.py")


deploy_tasks()
