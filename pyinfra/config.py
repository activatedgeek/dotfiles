import os
import sys
from pathlib import Path

from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from diskcache import Cache
from pyinfra.api import config, exceptions

from pyinfra import logger


def setup_secrets():
    try:
        inventory_file = Path([arg for arg in sys.argv if arg.startswith("inventories") and Path(arg).is_file()][0])
        inventory_name = Path(inventory_file).stem
    except IndexError as e:
        raise exceptions.DeployError("Missing inventory file") from e

    cache = Cache(config.CACHE_PATH)

    secrets = cache.get(f"secrets/bw/{inventory_name}")
    if secrets is None:
        bws_access_token = os.getenv("BWS_ACCESS_TOKEN")
        bws_org_id = os.getenv("BWS_ORG_ID")

        if bws_access_token is None or bws_org_id is None:
            raise exceptions.DeployError("Missing Bitwarden environment variables BWS_ACCESS_TOKEN / BWS_ORG_ID")

        logger.info("Loading inventory variables from Bitwarden Secrets.")

        client = BitwardenClient(
            client_settings_from_dict({"deviceType": DeviceType.SDK, "userAgent": "Python dotfiles"})
        )
        client.auth().login_access_token(bws_access_token)

        secrets = {}
        for secret in client.secrets().list(bws_org_id).data.data:
            secret = client.secrets().get(secret.id).data
            secrets[secret.key] = secret.value

        cache.set(f"secrets/bw/{inventory_name}", secrets, expire=7 * 24 * 60 * 60)

    return secrets


config.CACHE_PATH = Path(__file__).parent / ".pyinfra_cache"
config.FAIL_PERCENT = 0
config.SHELL = "bash"
config.SECRETS = setup_secrets()
