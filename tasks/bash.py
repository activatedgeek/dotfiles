from pyinfra import host, local
from pyinfra.api import deploy
from pyinfra.facts import server as server_facts
from pyinfra.operations import brew, files

from myinfra.operations import files as myfiles


@deploy("MacOS")
def apply_macos(teardown=False):
    brew.packages(
        name=f"{'Uni' if teardown else 'I'}nstall",
        packages=["bash", "bash-completion"],
        present=not teardown,
    )

    # server.shell(
    #     name="Change shell to bash",
    #     commands=[
    #         "chsh",
    #         "-s",
    #         f"{host.get_fact(brew_facts.BrewPrefix)}/bin/bash",
    #     ],
    #     _sudo=True,
    #     _use_sudo_login=True,
    # )


@deploy("Config")
def apply_config(teardown=False):
    files.directory(
        name="Profile Dir.",
        path=f"{host.get_fact(server_facts.Home)}/.local/profile",
        mode=700,
        present=True,
        recursive=True,
    )

    files.directory(
        name="Bin Dir.",
        path=f"{host.get_fact(server_facts.Home)}/.local/bin",
        mode=755,
        present=True,
        recursive=True,
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Profile",
        src="files/bash/.bash_profile",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.bash_profile",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Env",
        src="templates/bash/.bash_env.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.bash_env",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        inventory_hostname=host.name.split("/")[-1],
        git_name=local.shell("id -F"),
        git_email=host.data.email,
        term=host.data.get("term", None),
        store_home=host.data.get("store_home", None),
    )

    myfiles.template(
        name=f"{'Remove ' if teardown else ''}Secrets Env",
        src="templates/bash/.secrets_env.j2",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.secrets_env",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
        ## Jinja2 Variables.
        use_export=True,
        goatcounter_site=host.data.get("goatcounter_site", None),
        mapbox_access_token=host.data.get("mapbox_access_token", None),
        cloudflare_api_key=host.data.get("cloudflare_api_key", None),
        discord_webhook_token=host.data.get("discord_webhook_token", None),
        wandb_api_key=host.data.get("wandb_api_key", None),
        wandb_username=host.data.get("wandb_username", None),
        wandb_entity=host.data.get("wandb_entity", None),
        hf_token=host.data.get("hf_token", None),
        openai_api_key=host.data.get("openai_api_key", None),
        google_gemini_api_key=host.data.get("gemini_api_key", None),
        exa_api_key=host.data.get("exa_api_key", None),
        nvidia_api_key=host.data.get("nvidia_api_key", None),
        docker_hub_username=host.data.get("docker_hub_username", None),
        docker_hub_password=host.data.get("docker_hub_password", None),
        hcloud_token=host.data.get("hcloud_token", None),
        gitlab_token=host.data.get("gitlab_token", None),
        brave_api_key=host.data.get("brave_api_key", None),
    )

    myfiles.copy(
        name=f"{'Remove ' if teardown else ''}Aliases",
        src="files/bash/.bash_aliases",
        dest=f"{host.get_fact(server_facts.Home)}/.local/profile/.bash_aliases",
        mode=600,
        create_remote_dir=False,
        present=not teardown,
    )

    files.line(
        name=f"{'Remove' if teardown else 'Add'} Profile",
        path=f"{host.get_fact(server_facts.Home)}/.bash_profile",
        line=f"source {host.get_fact(server_facts.Home)}/.local/profile/.bash_profile",
        ensure_newline=True,
        present=not teardown,
    )

    if teardown:
        files.file(
            name="Remove History",
            path=f"{host.get_fact(server_facts.Home)}/.bash_history",
            present=False,
        )


def apply():
    teardown = host.data.get("teardown", False)
    kernel = host.get_fact(server_facts.Kernel)
    if kernel == "Darwin":
        apply_macos(teardown=teardown)

    apply_config(teardown=teardown)


apply()
