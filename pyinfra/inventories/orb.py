from myinfra.inventory import Inventory
from pyinfra.api import config

inventory = Inventory(
    vars=dict(
        term="xterm-256color",
    ),
    # Preserve the orb's managed Git identity, authentication, and SSH configuration.
    skip_tasks={"git", "micro", "micromamba", "opencode", "pueue", "ssh"},
    binary_versions=config.BINARY_VERSIONS,
)

inventory.hosts = [Inventory.Host(name="@local")]
inventory.groups = [Inventory.Group(name="linux", hosts={"@local"})]

globals().update(inventory.resolve())
