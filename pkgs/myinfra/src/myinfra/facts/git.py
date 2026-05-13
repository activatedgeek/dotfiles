from pyinfra.api.facts import FactBase


class GitLFSBinary(FactBase):
    def requires_command(self, *_, **__):
        return "command"

    def command(self, path: str | None = None):
        if path:
            return f'test -x {path} && echo "{path}" || true'
        return "command -v git-lfs || true"

    def process(self, output):
        return "".join(output).strip()


class GitXetBinary(FactBase):
    def requires_command(self, *_, **__):
        return "command"

    def command(self, path: str | None = None):
        if path:
            return f'test -x {path} && echo "{path}" || true'
        return "command -v git-xet || true"

    def process(self, output):
        return "".join(output).strip()
