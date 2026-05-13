from pyinfra.api.facts import FactBase


class SbatchBinary(FactBase):
    def requires_command(self, *_, **__):
        return "command"

    def command(self):
        return "command -v sbatch || true"

    def process(self, output):
        return "".join(output).strip()
