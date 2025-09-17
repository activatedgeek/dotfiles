from pathlib import Path

from pyinfra import host
from pyinfra.api import exceptions, operation
from pyinfra.api.command import QuoteString, StringCommand
from pyinfra.facts import server as server_facts


@operation()
def unzip(path):
    if host.get_fact(server_facts.Which, command="unzip"):
        yield StringCommand("unzip", "-o", QuoteString(path), "-d", QuoteString(Path(path).parent))
    else:
        raise exceptions.OperationError("unzip executable not found.")


@operation()
def untar(path, flags=None):
    if host.get_fact(server_facts.Which, command="tar"):
        yield StringCommand(
            "tar",
            f"-x{flags or ''}f",
            QuoteString(path),
            "-C",
            QuoteString(Path(path).parent),
        )
    else:
        raise exceptions.OperationError("tar executable not found.")
