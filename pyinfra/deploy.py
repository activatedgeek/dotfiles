from pathlib import Path

from myinfra.utils import load_task_module

from pyinfra import host, logger


def main():
    if host.data.get("skip_host", False):
        logger.warning(f"Skipping {host.name}.")
        return

    all_tasks = set(sorted([d.stem for d in (Path(__file__).parent / "tasks").iterdir() if d.is_dir()]))
    all_tasks -= host.data.get("skip_tasks", set())
    if host.data.get("apply_tasks"):
        all_tasks &= set(host.data.get("apply_tasks").split(","))

    for task in all_tasks:
        task, _ = load_task_module(task, f"tasks/{task}/apply.py")
        if callable(getattr(task, "apply", None)):
            task.apply()


main()
