from pyinfra import local


def deploy_tasks():
    for task in [
        "bash",
        "bottom",
        "git",
        "jq",
        "micro",
        "pueue",
        "python",
        "rclone",
        "slurm",
        "starship",
        "tmux",
        "uv",
        "vscode",
        "wandb",
    ]:
        local.include(f"tasks/{task}.py")


deploy_tasks()
