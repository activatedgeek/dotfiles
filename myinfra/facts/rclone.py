from pyinfra import host
from pyinfra.api import exceptions
from pyinfra.facts import server as server_facts, files as file_facts
from pyinfra.api.facts import FactBase


class Obscure(FactBase):
    def command(self, password, executable=None):
        if host.get_fact(file_facts.File, "~/.local/bin/rclone"):
            executable = "~/.local/bin/rclone"

        if executable is None:
            if not host.get_fact(server_facts.Which, command="rclone"):
                raise exceptions.FactError("rclone executable not found.")
            executable = "rclone"

        return f"echo {password} | {executable} obscure -"

    def process(self, output):
        return "".join(output).strip()
