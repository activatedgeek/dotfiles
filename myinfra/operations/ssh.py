from pyinfra import host
from pyinfra.api import operation
from pyinfra.api.command import QuoteString, StringCommand

from ..facts import ssh as ssh_facts


@operation()
def add(src, present=True):
    fingerprint = host.get_fact(ssh_facts.Fingerprint, src)
    is_added = host.get_fact(ssh_facts.AgentKey, fingerprint)

    if not is_added and present:
        yield StringCommand("ssh-add", "--apple-use-keychain", QuoteString(src))
    elif is_added and not present:
        yield StringCommand("ssh-add", "-d", QuoteString(src))
