import re

from pyinfra.api.facts import FactBase


class HwModel(FactBase):
    def requires_command(self, *_, **__):
        return "sysctl"

    def command(self):
        return "sysctl -n hw.model 2>/dev/null || true"

    def process(self, output):
        output = "".join(output).strip()

        pattern = re.compile(r"^([A-Za-z]+?)(\d+),(\d+)$")
        match = pattern.match(output)
        if match:
            family, major, minor = match.groups()
            return family, major, minor


class MacOSVM(HwModel):
    def process(self, output):
        output = super().process(output)

        if output:
            family, *_ = output

            return family.lower() in ["virtualmac"]

        return False
