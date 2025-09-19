from pyinfra.api.facts import FactBase


class EnrootExists(FactBase):
    def requires_command(self, *_, **__):
        return "command"

    def command(self):
        return "command -v enroot || true"

    def process(self, output):
        return "".join(output).strip()
