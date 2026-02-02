from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import files

import myinfra.facts.enroot as enroot_facts
import myinfra.operations.files as myfiles


@deploy("Config")
def apply_config(teardown=False):
    remote_home = host.get_fact(server_facts.Home)

    files.directory(
        name=f"{'Remove ' if teardown else ''}Directory",
        path=f"{remote_home}/.config/enroot",
        mode=700,
        present=not teardown,
        recursive=True,
    )

    for d in ["mounts.d", "environ.d"]:
        files.directory(
            name=f"{'Remove ' if teardown else ''}{d}",
            path=f"{remote_home}/.config/enroot/{d}",
            mode=700,
            present=not teardown,
            recursive=True,
        )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''} Credentials",
        src="templates/enroot/.credentials.j2",
        dest=f"{remote_home}/.config/enroot/.credentials",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        docker_hub_username=host.data.get("docker_hub_username"),
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}mkenroot",
        src="files/enroot/mkenroot.sh",
        dest=f"{remote_home}/.local/bin/mkenroot",
        mode=755,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Default Mounts",
        src="templates/enroot/mounts.d/default.fstab.j2",
        dest=f"{remote_home}/.config/enroot/mounts.d/default.fstab",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        extra_mounts=host.data.get("enroot_mounts", []),
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Default Env",
        src="templates/enroot/environ.d/default.env.j2",
        dest=f"{remote_home}/.config/enroot/environ.d/default.env",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        extra_env=host.data.get("enroot_env", {}),
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}ML Secrets Env",
        src="templates/bash/.ml_secrets_env.j2",
        dest=f"{remote_home}/.config/enroot/environ.d/ml_secrets.env",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        use_export=False,
        azure_openai_api_key=host.data.get("azure_openai_api_key"),
        bbh_nvidia_api_key=host.data.get("bbh_nvidia_api_key"),
        brave_api_key=host.data.get("brave_api_key"),
        exa_api_key=host.data.get("exa_api_key"),
        google_search_engine_id=host.data.get("google_search_engine_id"),
        google_search_api_key=host.data.get("google_search_api_key"),
        hf_token=host.data.get("hf_token"),
        nvidia_api_key=host.data.get("nvidia_api_key"),
        openai_client_id=host.data.get("openai_client_id"),
        openai_client_secret=host.data.get("openai_client_secret"),
        tavily_api_key=host.data.get("tavily_api_key"),
        wandb_api_key=host.data.get("wandb_api_key"),
        wandb_username=host.data.get("wandb_username"),
        wandb_entity=host.data.get("wandb_entity"),
    )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    enroot_exists = host.get_fact(enroot_facts.EnrootExists)
    if kernel == "Linux" and enroot_exists:
        apply_config(teardown=teardown)


apply()
