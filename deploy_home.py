from pyinfra import local, host
from pyinfra.operations import server


def deploy_tasks():
    tasks = [
        "bash",
        "bitwarden",
        "cleanmymac",
        "cloudflare",
        "discord",
        "docker",
        "filen",
        "ghostty",
        "git",
        "jq",
        "mega",
        "micro",
        "netnewswire",
        "node",
        "obsidian",
        "pandoc",
        "python",
        "rclone",
        "slack",
        "spotify",
        "ssh",
        "starship",
        "tailscale",
        "uv",
        "vscode",
        "wandb",
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
