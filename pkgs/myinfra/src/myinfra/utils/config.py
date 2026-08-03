import inspect
from pathlib import Path

from diskcache import Cache

from pyinfra import logger

from .binary import Binary
from .tasks import load_task_module


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
