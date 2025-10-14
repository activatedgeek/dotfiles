from packaging.requirements import Requirement
from packaging.version import Version
from pyinfra import host
from pyinfra.api import operation
from pyinfra.api.command import StringCommand

from ..facts import uv as uv_facts


@operation()
def venv(path, python_version="3.11", requirements=None, binary_path=None, present=True):
    binary_path = binary_path or "uv"
    venv_path = path + "/.venv"

    exists = host.get_fact(uv_facts.VenvExists, path=venv_path)

    if present:
        if not exists:
            yield StringCommand(binary_path, "--quiet", "venv", "--python", python_version, venv_path)

        if requirements:
            installed = host.get_fact(uv_facts.PipPackages, path=path, binary_path=binary_path)
            requirements = [Requirement(r) for r in requirements]

            def is_pending(r):
                p = False
                p |= r.name not in installed
                p |= r.name in installed and Version(installed[r.name]) not in r.specifier
                return p

            pending_requirements = [str(r) for r in requirements if is_pending(r)]
            if pending_requirements:
                yield StringCommand(binary_path, "pip", "install", "--quiet", *pending_requirements, _chdir=path)

    if not present and exists:
        yield StringCommand("rm", "-r", venv_path)
