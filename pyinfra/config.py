import json
import os
import sys
from pathlib import Path

from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from pyinfra.api import config, exceptions

from pyinfra import logger

PYINFRA_CACHE_PATH = Path(__file__).parent / ".pyinfra_cache"


def setup_inventory_vars():
    try:
        inventory_file = Path([arg for arg in sys.argv if arg.startswith("inventories") and Path(arg).is_file()][0])
        inventory_name = Path(inventory_file).stem
    except IndexError as e:
        raise exceptions.DeployError("Missing inventory file") from e

    cache_file = PYINFRA_CACHE_PATH / "inventories" / inventory_name / "vars.json"
    cache_file.parent.mkdir(exist_ok=True, parents=True, mode=0o700)

    if not cache_file.is_file():
        bws_access_token = os.getenv("BWS_ACCESS_TOKEN")
        bws_org_id = os.getenv("BWS_ORG_ID")

        if bws_access_token is None or bws_org_id is None:
            raise exceptions.DeployError("Missing Bitwarden environment variables BWS_ACCESS_TOKEN / BWS_ORG_ID")

        logger.info("Loading inventory variables from Bitwarden Secrets.")

        client = BitwardenClient(
            client_settings_from_dict({"deviceType": DeviceType.SDK, "userAgent": "Python dotfiles"})
        )
        client.auth().login_access_token(bws_access_token)

        all_secrets = {}
        for secret in client.secrets().list(bws_org_id).data.data:
            secret = client.secrets().get(secret.id).data
            all_secrets[secret.key] = secret.value

        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w") as f:
            f.write(json.dumps(all_secrets, indent=2))

    with open(cache_file, "r") as f:
        all_secrets = json.load(f)

    return all_secrets


config.FAIL_PERCENT = 0
config.PARALLEL = 10
config.SHELL = "bash"
config.INVENTORY_VARS = setup_inventory_vars()
