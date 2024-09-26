import json
from pyinfra.api.facts import FactBase


class BuildX(FactBase):
    def requires_command(self, *_, **__):
        return "cat"

    def command(self):
        return "cat ~/.docker/config.json"

    def process(self, output):
        config = json.loads("".join(output).strip())
        aliases = config.get("aliases", {})
        builder = aliases.get("builder", None)
        return builder == "buildx"
