import os
from pathlib import Path

import requests
from myinfra.utils.config import get_latest_binary_versions
from pyinfra.api import config

from pyinfra import logger

config.CACHE_HOME = Path(os.getenv("PYINFRA_CACHE_HOME", Path(__file__).parent / ".pyinfra_cache"))
config.CACHE_TTL = int(os.getenv("PYINFRA_CACHE_TTL", 24 * 60 * 60))
config.SHELL = "bash"

try:
    config.BINARY_VERSIONS = get_latest_binary_versions(
        Path(__file__).parent / "tasks", cache_dir=config.CACHE_HOME, cache_ttl=config.CACHE_TTL
    )
except requests.exceptions.HTTPError as err:
    logger.exception(err)
    config.BINARY_VERSIONS = {}
