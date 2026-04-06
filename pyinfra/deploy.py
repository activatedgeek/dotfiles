from pathlib import Path

from myinfra.utils import load_task_module

from pyinfra import host, logger


def main():
    if host.data.get("skip_host", False):
        logger.warning(f"Skipping {host.name}.")
        return

    all_tasks = set(sorted([d.stem for d in (Path(__file__).parent / "tasks").iterdir() if d.is_dir()]))

    if host.data.get("skip_tasks"):
        skip_tasks = set(
            [
                t.strip()
                for t in (
                    host.data.skip_tasks.split(",") if isinstance(host.data.skip_tasks, str) else host.data.skip_tasks
                )
                if t.strip()
            ]
        )
        all_tasks -= skip_tasks

    if host.data.get("apply_tasks"):
        apply_tasks = set(
            [
                t.strip()
                for t in (
                    host.data.apply_tasks.split(",")
                    if isinstance(host.data.apply_tasks, str)
                    else host.data.apply_tasks
                )
                if t.strip()
            ]
        )
        all_tasks &= apply_tasks

    for task in all_tasks:
        task, _ = load_task_module(task, f"tasks/{task}/apply.py")

        if callable(getattr(task, "pre_check", None)) and not task.pre_check():
            continue

        if callable(getattr(task, "apply", None)):
            task.apply()


main()
