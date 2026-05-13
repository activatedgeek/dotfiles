import json

from pyinfra.api.facts import FactBase


class BuildX(FactBase):
    def requires_command(self, *_, **__):
        return "cat"

    def command(self):
        return "cat ~/.docker/config.json || true"

    def process(self, output):
        output = "".join(output).strip()
        if not output:
            return False
        config = json.loads(output)
        aliases = config.get("aliases", {})
        builder = aliases.get("builder", None)
        return builder == "buildx"


class DockerBinary(FactBase):
    def requires_command(self, *_, **__):
        return "command"

    def command(self, path: str | None = None):
        if path:
            return f'test -x {path} && echo "{path}" || true'
        return "command -v docker || true"

    def process(self, output):
        return "".join(output).strip()
