import importlib
from pathlib import Path


def load_task_module(name: str, path: str | Path):
    task_spec = importlib.util.spec_from_file_location(f"pyinfra._dynamic.tasks.{name}", path)
    task = importlib.util.module_from_spec(task_spec)
    task_spec.loader.exec_module(task)

    return task, task_spec
