from myinfra.inventory import Inventory

inventory = Inventory()
inventory.hosts = [
    Inventory.Host(
        name="@local",
        vars=dict(
            email="test@example.com",
        ),
    ),
]

globals().update(inventory.resolve())
