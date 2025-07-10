from pyinfra import local


def deploy_tasks():
    for task in [
        "bash",
        "bottom",
        "docker",
        "discord",
        "enroot",
        "ghostty",
        "git",
        "jq",
        "micro",
        "python",
        "rclone",
        "slurm",
        "ssh",
        "starship",
        "tmux",
        "uv",
        "vscode",
        "wandb",
    ]:
        local.include(f"tasks/{task}.py")


deploy_tasks()
