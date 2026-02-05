from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import server


@deploy("Home")
def apply_config_home(teardown=False):
    if host.name == "@local":
        ## Remove logs every hour.
        server.crontab(
            name="Cron Logs",
            command="rm -rf /tmp/*.log",
            minute="0",
            hour="12",
            month="*",
            day_of_week="*",
            day_of_month="*",
            present=not teardown,
        )


@deploy("Config")
def apply_config(teardown=False):
    if host.data.get("org") == "home":
        apply_config_home(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)

    apply_config(teardown=teardown)


apply()
