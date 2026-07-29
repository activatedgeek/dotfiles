import inspect
import os
import sys
from pathlib import Path

from bitwarden_sdk import BitwardenClient, DeviceType, client_settings_from_dict
from diskcache import Cache
from pyinfra.api import exceptions

from pyinfra import logger

from .binary import Binary
from .tasks import load_task_module


def get_secrets(cache_dir: str | Path | None = None, cache_ttl: int = 24 * 60 * 60) -> dict:
    try:
        inventory_file = Path([arg for arg in sys.argv if arg.startswith("inventories") and Path(arg).is_file()][0])
        inventory_name = Path(inventory_file).stem
    except IndexError as err:
        raise RuntimeError("Missing inventory file") from err

    cache = Cache(cache_dir)

    secrets = cache.get(f"secrets/bw/{inventory_name}")
    if secrets is None:
        bws_access_token = os.getenv("BWS_ACCESS_TOKEN")
        bws_org_id = os.getenv("BWS_ORG_ID")

        if bws_access_token is None or bws_org_id is None:
            raise exceptions.DeployError("Missing Bitwarden environment variables BWS_ACCESS_TOKEN / BWS_ORG_ID")

        logger.info("Loading Bitwarden Secrets...")

        client = BitwardenClient(
            client_settings_from_dict({"deviceType": DeviceType.SDK, "userAgent": "Python dotfiles"})
        )
        client.auth().login_access_token(bws_access_token)

        secrets = {}
        for secret in client.secrets().list(bws_org_id).data.data:
            secret = client.secrets().get(secret.id).data
            secrets[secret.key] = secret.value

        cache.set(f"secrets/bw/{inventory_name}", secrets, expire=cache_ttl)

    return secrets


def get_latest_binary_versions(
    tasks_dir: str | Path, cache_dir: str | Path | None = None, cache_ttl: int = 24 * 60 * 60
) -> dict:
    tasks_dir = Path(tasks_dir)

    binary_cls_map = {}
    for task in set(sorted([d.stem for d in tasks_dir.iterdir() if d.is_dir()])):
        task, _ = load_task_module(task, tasks_dir / task / "apply.py")
        for _, cls in inspect.getmembers(task, inspect.isclass):
            if cls is Binary or not issubclass(cls, Binary):
                continue

            binary_cls_map[cls.__name__] = cls

    cache = Cache(cache_dir)

    latest_versions = cache.get("versions/latest")
    if latest_versions is None:
        logger.info("Fetching latest binary versions...")

        latest_versions = {k: cls("amd64").latest for k, cls in binary_cls_map.items()}
        cache.set("versions/latest", latest_versions, expire=cache_ttl)

    for k, cls in binary_cls_map.items():
        logger.debug(f"Binary {cls.__name__.lower()}: {latest_versions[k]} (Current: {cls.version})")

        if latest_versions[k] is not None:
            if cls.version != latest_versions[k]:
                logger.warning(
                    f"Update available for {cls.__name__.lower()}: {latest_versions[k]} (!= {cls.version})."
                )

    return latest_versions
