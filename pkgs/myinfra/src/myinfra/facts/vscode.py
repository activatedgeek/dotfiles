from pyinfra.api.facts import FactBase


class Extension(FactBase):
    def requires_command(self, *args, **kwargs):
        return "code"

    def command(self, extension):
        return f"code --list-extensions | grep -w {extension} | cat"

    def process(self, output):
        return output
