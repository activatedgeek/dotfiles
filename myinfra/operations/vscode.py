from pyinfra import host
from pyinfra.api import operation
from pyinfra.api.command import StringCommand


from ..facts import vscode as vscode_facts


@operation()
def extension(extension, present=True):
    exists = host.get_fact(vscode_facts.Extension, extension=extension)

    if present and not exists:
        yield StringCommand("code", "--install-extension", extension)

    if not present and exists:
        yield StringCommand("code", "--uninstall-extension", extension)
