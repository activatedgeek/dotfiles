from pyinfra import host
from pyinfra.api import FactBase


class HasSudoAccess(FactBase):
    sudo_groups = {"sudo", "wheel", "admin"}

    def requires_command(self, *args, **kwargs):
        return "groups"

    def command(self):
        return "groups"

    def process(self, output):
        groups = "".join(output).strip().split()
        in_group = any(g in self.sudo_groups for g in groups)
        if in_group:
            return host.data.get("sudo_password") is not None
        return False
