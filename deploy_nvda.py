from pyinfra import local


def deploy_tasks():
    for task in [
        "bash",
        "bottom",
        "discord",
        "enroot",
        "ghostty",
        "git",
        "jq",
        "micro",
        "nemo",
        "python",
        "rclone",
        "slurm",
        "ssh",
        "starship",
        "tmux",
        "uv",
        "wandb",
        "zed",
    ]:
        local.include(f"tasks/{task}.py")


deploy_tasks()
