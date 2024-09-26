from pyinfra.api.facts import FactBase


class BrewPrefix(FactBase):
    def requires_command(self, *_, **__):
        return "brew"

    def command(self):
        return "brew --prefix"

    def process(self, output):
        return "".join(output).strip()
