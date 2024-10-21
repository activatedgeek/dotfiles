from pyinfra.api.facts import FactBase


class SHA256Sum(FactBase):
    def requires_command(self, *_, **__):
        return "sha256sum"

    def command(self, path):
        return f"sha256sum {path}"

    def process(self, output):
        return "".join(output).strip().split()[0]
