import os
from pathlib import Path
from typing import ClassVar

from aim import Run as AimRun


class AimTracker:
    """Wrapper class for tracking runs via Aim."""

    config_key: ClassVar[str] = "config"

    runtime_config_key: ClassVar[str] = "rc"

    def __init__(
        self,
        run_hash: str | None = os.getenv("AIM_RUN_HASH"),
        repo: str | None = os.getenv("AIM_REPO"),
        experiment: str | None = os.getenv("AIM_EXPERIMENT"),
        name: str | None = None,
        tags: list[str] | None = None,
        log_system_params: bool = False,
        capture_terminal_logs: bool = False,
    ):
        if not repo:
            raise ValueError("Missing repo. Optionally, set AIM_REPO environment variable.")

        repo = Path(repo)

        self.run = AimRun(
            run_hash=run_hash,
            repo=repo,
            experiment=experiment if not run_hash else None,
            log_system_params=log_system_params,
            capture_terminal_logs=capture_terminal_logs,
        )

        if run_hash is None and name:
            self.name = name

        if tags:
            self.tags = tags

    @property
    def id(self):
        return self.run.hash

    @property
    def name(self):
        return self.run.name

    @name.setter
    def name(self, name: str):
        self.run.name = name

    @property
    def tags(self):
        return self.run.tags

    @tags.setter
    def tags(self, tags: list[str]):
        for t in tags:
            self.run.add_tag(t)

    @property
    def config(self):
        return self.run.get(self.config_key, {})

    @config.setter
    def config(self, new_config: dict):
        self.run[self.config_key] = {**self.config, **new_config}

    @property
    def rc(self):
        return self.run.get(self.runtime_config_key, {})

    @rc.setter
    def rc(self, new_runtime_config: dict):
        self.run[self.runtime_config_key] = {**self.rc, **new_runtime_config}

    def track(self, *args, **kwargs):
        self.run.track(*args, **kwargs)

    def nemo_run(self, experiment):
        def _parse_job_id(j):
            try:
                return int(j)
            except ValueError:
                return

        status = experiment.status(return_dict=True)

        self.rc = dict(
            nemo_run=self.rc.get("nemo_run", [])
            + [
                {
                    "id": experiment._id,
                    "executor": status[next(iter(status.keys()))]["executor"],
                    "dir": experiment._exp_dir,
                    "slurm_jobs_ids": [_parse_job_id(v["job_id"]) for _, v in status.items()],
                }
            ]
        )
