import importlib.util
from pathlib import Path

from pyinfra import host, logger


def main():
    if host.data.get("skip", False):
        logger.warning(f"Skipping {host.name}.")
        return

    all_tasks = sorted([d.stem for d in (Path(__file__).parent / "tasks").iterdir() if d.is_dir()])
    skip_tasks = host.data.get("skip_tasks", {})
    for task in filter(lambda t: t not in skip_tasks, all_tasks):
        task_spec = importlib.util.spec_from_file_location(f"pyinfra._dynamic.tasks.{task}", f"tasks/{task}/apply.py")
        task = importlib.util.module_from_spec(task_spec)
        task_spec.loader.exec_module(task)

        if callable(getattr(task, "apply", None)):
            task.apply()


main()
