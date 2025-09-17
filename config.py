import os
from pathlib import Path

from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from dotenv import dotenv_values
from pyinfra import logger
from pyinfra.api import config, exceptions


def setup_inventory_vars(env_file=".env", cache_file=".env.inventory"):
    if not Path(cache_file).is_file():
        if Path(env_file).is_file():
            bws_env = dotenv_values(env_file)
            bws_access_token = bws_env.get("BWS_ACCESS_TOKEN", None)
            bws_org_id = bws_env.get("BWS_ORG_ID", None)
        else:
            bws_access_token = os.getenv("BWS_ACCESS_TOKEN", None)
            bws_org_id = os.getenv("BWS_ORG_ID", None)

        if bws_access_token is None or bws_org_id is None:
            raise exceptions.DeployError("Missing Bitwarden environment variables BWS_ACCESS_TOKEN / BWS_ORG_ID")

        logger.info("Loading inventory variables from Bitwarden Secrets.")

        client = BitwardenClient(
            client_settings_from_dict({"deviceType": DeviceType.SDK, "userAgent": "Python dotfiles"})
        )
        client.auth().login_access_token(bws_access_token)

        all_secrets = []
        for secret in client.secrets().list(bws_org_id).data.data:
            secret = client.secrets().get(secret.id).data
            all_secrets.append(f"{secret.key}='{secret.value}'\n")

        with open(cache_file, "w") as f:
            f.writelines(all_secrets)

    return dotenv_values(cache_file)


config.FAIL_PERCENT = 0
config.PARALLEL = 10
config.SHELL = "bash"
config.INVENTORY_VARS = setup_inventory_vars()
