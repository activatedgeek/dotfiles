from pyinfra.api.facts import FactBase


class DpkgArch(FactBase):
    def requires_command(self, *_, **__):
        return "dpkg"

    def command(self):
        return "dpkg --print-architecture"

    def process(self, output):
        return "".join(output).strip()
