from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, brew
from pyinfra.facts import server as server_facts

from myinfra.operations import files as myfiles


## https://downloads.rclone.org/
rclone_version = "1.67.0"


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["rclone"],
        present=not teardown,
    )


@deploy("Linux")
def apply_linux(teardown=False):
    myfiles.download(
        name=f"{'Uni' if teardown else 'I'}nstall",
        src=f"https://downloads.rclone.org/v{rclone_version}/rclone-v{rclone_version}-linux-amd64.zip",
        src_dir=f"rclone-v{rclone_version}-linux-amd64",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/rclone",
        present=not teardown,
        mode=755,
    )


@deploy("NYU")
def apply_config_nyu(teardown=False):
    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Config",
        src="templates/rclone/nyu-rclone.conf.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.config/rclone/rclone.conf",
        present=not teardown,
        mode=600,
        create_remote_dir=False,
        rclone_nyu_drive_client_id=host.data.rclone_nyu_drive_client_id,
        rclone_nyu_drive_client_secret=host.data.rclone_nyu_drive_client_secret,
        rclone_nyu_drive_access_token=host.data.rclone_nyu_drive_access_token,
        rclone_nyu_drive_refresh_token=host.data.rclone_nyu_drive_refresh_token,
        rclone_nyu_drive_expiry=host.data.rclone_nyu_drive_expiry,
    )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{host.get_fact(server_facts.Home)}/.config/rclone",
        present=not teardown,
        mode=700,
    )

    if host.data.get("org", "") == "nyu":
        apply_config_nyu(teardown=teardown)


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)
    elif kernel == "Linux":
        apply_linux(teardown=teardown)

    apply_config(teardown=teardown)


apply()
