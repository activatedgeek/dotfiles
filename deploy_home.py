from pyinfra import host, local
from pyinfra.operations import server


def deploy_tasks():
    tasks = [
        "bash",
        "bitwarden",
        "cloudflare",
        "discord",
        "docker",
        "ghostty",
        "git",
        "jq",
        "mega",
        "micro",
        "mole",
        "netnewswire",
        "node",
        "obsidian",
        "python",
        "rclone",
        "slack",
        "ssh",
        "starship",
        "tailscale",
        "uv",
        "wandb",
        "zed",
    ]

    for t in tasks:
        local.include(f"tasks/{t}.py")

    ## Remove logs every hour.
    server.crontab(
        name="Cron Logs",
        command="rm -rf /tmp/*.log",
        minute="0",
        hour="12",
        month="*",
        day_of_week="*",
        day_of_month="*",
        present=not host.data.get("teardown", False),
    )


deploy_tasks()
