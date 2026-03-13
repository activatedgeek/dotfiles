import json

from pyinfra.api.facts import FactBase


class VenvExists(FactBase):
    def requires_command(self, *_, **__):
        return "test"

    def command(self, path):
        return f'[ -d "{path}" ] && echo "{path}" || true'

    def process(self, output):
        return "".join(output).strip()


class PipPackages(FactBase):
    def requires_command(self, *_, **__):
        return "test"

    def command(self, path, binary_path=None):
        binary_path = binary_path or "uv"
        return f"{binary_path} --quiet --directory {path} pip list --format json"

    def process(self, output):
        packages = json.loads("".join(output))
        return {p["name"]: p["version"] for p in packages}
