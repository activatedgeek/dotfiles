from pyinfra.api.facts import FactBase


class Fingerprint(FactBase):
    def requires_command(self, *args, **kwargs):
        return "ssh-keygen"

    def command(self, key_file_path):
        return f"ssh-keygen -lf {key_file_path} | awk '{{print $2}}'"

    def process(self, output):
        return "".join(output).strip()


class AgentKey(FactBase):
    def requires_command(self, *args, **kwargs):
        return "ssh-add"

    def command(self, fingerprint):
        return f"ssh-add -l | grep -w {fingerprint} | cat"

    def process(self, output):
        if len(output):
            return True
        return None
