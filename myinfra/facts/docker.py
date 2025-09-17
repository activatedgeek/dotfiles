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
