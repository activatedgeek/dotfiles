from pyinfra.api.facts import FactBase
from pyinfra.facts import server as server_facts

from pyinfra import host


class DpkgArch(FactBase):
    def requires_command(self, *_, **__):
        return "dpkg"

    def command(self):
        return "dpkg --print-architecture"

    def process(self, output):
        return "".join(output).strip()


class UserFullName(FactBase):
    def requires_command(self, *_, **__):
        kernel = host.get_fact(server_facts.Kernel)
        if kernel == "Darwin":
            return "id"
        return "getent"

    def command(self):
        kernel = host.get_fact(server_facts.Kernel)
        if kernel == "Darwin":
            return "id -F"
        return "getent passwd $USER | cut -d: -f5"

    def process(self, output):
        return "".join(output).strip()
