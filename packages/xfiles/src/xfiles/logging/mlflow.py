import json
import os
import tempfile
import warnings
from pathlib import Path
from typing import ClassVar, Optional

from mlflow.entities import Experiment, Run
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient


class MLflowTracker:
    """Wrapper class for tracking runs via MLflow."""

    runtime_config: ClassVar[str] = "rc.json"

    def __init__(
        self,
        run_id: Optional[str] = os.getenv("MLFLOW_RUN_ID"),
        tracking_uri: Optional[str] = os.getenv("MLFLOW_TRACKING_URI"),
        experiment: Optional[str] = os.getenv("MLFLOW_EXPERIMENT"),
        name: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ):
        if not tracking_uri:
            raise ValueError("Missing repo/tracking URI. Optionally, set MLFLOW_TRACKING_URI environment variable.")

        self.client = MlflowClient(tracking_uri=tracking_uri)

        experiment: Experiment = self.client.get_experiment_by_name(experiment) or self.client.get_experiment(
            self.client.create_experiment(experiment)
        )
        self.experiment_id = experiment.experiment_id

        run: Run = (
            self.client.get_run(run_id)
            if run_id
            else self.client.create_run(experiment_id=self.experiment.experiment_id, run_name=name)
        )
        self.id = run.info.run_id

        if tags:
            self.tags = tags

    @property
    def experiment(self) -> Experiment:
        return self.client.get_experiment(self.experiment_id)

    @property
    def run(self) -> Run:
        return self.client.get_run(self.id)

    @property
    def name(self) -> Optional[str]:
        return self.tags.get("mlflow.runName")

    @name.setter
    def name(self, name: str):
        self.client.set_tag(self.id, "mlflow.runName", name)

    @property
    def tags(self) -> list[str]:
        return [k for k in self.run.data.tags.keys()]

    @tags.setter
    def tags(self, tags: list[str]):
        for t in tags:
            self.client.set_tag(self.id, t, True)

    @property
    def config(self) -> dict:
        return self.run.data.params

    @config.setter
    def config(self, new_config: dict):
        for k in set(self.config.keys()).intersection(new_config.keys()):
            if self.config[k] != new_config[k]:
                warnings.warn(f'Cannot overwrite existing key "{k}".', RuntimeWarning)
            new_config.pop(k)

        for k, v in new_config.items():
            self.client.log_param(self.id, k, v, synchronous=True)

    @property
    def rc(self) -> dict:
        with tempfile.TemporaryDirectory() as td:
            try:
                local_path = self.client.download_artifacts(
                    run_id=self.id,
                    path=self.runtime_config,
                    dst_path=td,
                )
                with open(local_path) as f:
                    return json.load(f)
            except MlflowException:
                return {}

    @rc.setter
    def rc(self, new_runtime_config: dict):
        merged = {**self.rc, **(new_runtime_config or {})}
        with tempfile.TemporaryDirectory() as td:
            tmp_file = Path(td) / self.runtime_config
            with open(tmp_file, "w") as f:
                json.dump(merged, f)
            self.client.log_artifact(
                run_id=self.id,
                local_path=tmp_file,
            )
