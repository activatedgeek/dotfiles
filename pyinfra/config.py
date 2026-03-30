import inspect
import os
import sys
from pathlib import Path

from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from diskcache import Cache
from myinfra.utils import Binary, load_task_module
from pyinfra.api import config, exceptions

from pyinfra import logger


def get_secrets():
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

        logger.info("Loading inventory variables from Bitwarden Secrets...")

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


def get_latest_binary_versions():
    cache = Cache(config.CACHE_PATH)

    latest_versions = cache.get("versions/latest")
    if latest_versions is None:
        latest_versions = {}

        for task in set(sorted([d.stem for d in (Path(__file__).parent / "tasks").iterdir() if d.is_dir()])):
            task, _ = load_task_module(task, f"tasks/{task}/apply.py")
            for _, cls in inspect.getmembers(task, inspect.isclass):
                if cls is Binary or not issubclass(cls, Binary):
                    continue

                latest_versions[cls.__name__] = cls

        logger.info(f"Fetching latest versions for: ({', '.join(sorted(latest_versions.keys()))})...")
        latest_versions = {k: cls("amd64").latest for k, cls in latest_versions.items()}

        cache.set("versions/latest", latest_versions, expire=7 * 24 * 60 * 60)

    return latest_versions


config.CACHE_PATH = Path(__file__).parent / ".pyinfra_cache"
config.FAIL_PERCENT = 0
config.SHELL = "bash"
config.SECRETS = get_secrets()
config.BINARY_VERSIONS = get_latest_binary_versions()
