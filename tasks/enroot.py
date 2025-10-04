from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

import myinfra.facts.enroot as enroot_facts
import myinfra.operations.files as myfiles


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{host.get_fact(server_facts.Home)}/.config/enroot",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    for d in ["mounts.d", "environ.d"]:
        files.directory(
            name=f"{'Remove ' if teardown else ''}{d}",
            path=f"{host.get_fact(server_facts.Home)}/.config/enroot/{d}",
            mode=700,
            present=not teardown,
            recursive=True,
        )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="files/enroot/.credentials",
        dest=f"{host.get_fact(server_facts.Home)}/.config/enroot/.credentials",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}mkenroot",
        src="files/enroot/mkenroot.sh",
        dest=f"{host.get_fact(server_facts.Home)}/.local/bin/mkenroot",
        mode=755,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''} Default Mounts",
        src="templates/enroot/mounts.d/default.fstab.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.config/enroot/mounts.d/default.fstab",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        store_home=host.data.store_home,
        extra_mounts=host.data.get("enroot_mounts", []),
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Secrets",
        src="templates/bash/.secrets_env.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.config/enroot/environ.d/secrets.env",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        use_export=False,
        discord_webhook_token=host.data.get("discord_webhook_token", None),
        wandb_api_key=host.data.get("wandb_api_key", None),
        wandb_username=host.data.get("wandb_username", None),
        wandb_entity=host.data.get("wandb_entity", None),
        hf_token=host.data.get("hf_token", None),
        openai_api_key=host.data.get("openai_api_key", None),
        google_gemini_api_key=host.data.get("gemini_api_key", None),
        exa_api_key=host.data.get("exa_api_key", None),
        nvidia_api_key=host.data.get("nvidia_api_key", None),
        gitlab_token=host.data.get("gitlab_token", None),
        brave_api_key=host.data.get("brave_api_key", None),
    )

    files.directory(
        name="Images directory",
        path=f"{host.data.store_home.replace('${USER}', host.data.ssh_user)}/images",
        present=True,
    )

    files.link(
        name=f"{'Remove ' if teardown else ''}Images Symlink",
        path=f"{host.get_fact(server_facts.Home)}/images",
        target=f"{host.data.store_home.replace('${USER}', host.data.ssh_user)}/images",
        present=not teardown,
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    enroot_exists = host.get_fact(enroot_facts.EnrootExists)
    if kernel == "Linux" and enroot_exists:
        apply_config(teardown=teardown)


apply()
