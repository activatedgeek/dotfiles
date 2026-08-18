from dataclasses import dataclass, field
from typing import Any


@dataclass
class InventoryHost:
    name: str
    host: str | None = None
    vars: dict[str, Any] = field(default_factory=dict)
    skip_tasks: set[str] = field(default_factory=set)

    def resolve(self) -> tuple[str, dict[str, Any]]:
        return self.name, {**self.vars, "skip_tasks": self.skip_tasks}


@dataclass
class InventoryGroup:
    name: str
    hosts: list[InventoryHost]
    vars: dict[str, Any] = field(default_factory=dict)
    skip_tasks: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        host_names = [host.name for host in self.hosts]
        if len(host_names) != len(set(host_names)):
            raise ValueError(f"Duplicate host name in inventory group {self.name!r}.")

    def resolve(self) -> tuple[list[tuple[str, dict[str, Any]]], dict[str, Any]]:
        hosts = [
            (
                host.name,
                {
                    **self.vars,
                    **host.vars,
                    "skip_tasks": host.skip_tasks | self.skip_tasks,
                },
            )
            for host in self.hosts
        ]
        return hosts, {}


@dataclass
class Inventory:
    groups: list[InventoryGroup]
    vars: dict[str, Any] = field(default_factory=dict)
    skip_tasks: set[str] = field(default_factory=set)
    binary_versions: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        group_names = [group.name for group in self.groups]
        if "all" in group_names:
            raise ValueError("The 'all' group name is reserved.")
        if len(group_names) != len(set(group_names)):
            raise ValueError("Duplicate group name in inventory.")

    def resolve(self) -> dict[str, tuple[list[Any], dict[str, Any]]]:
        resolved = {}
        for group in self.groups:
            hosts, _ = group.resolve()
            resolved[group.name] = (
                [
                    (
                        name,
                        {
                            **self.vars,
                            **vars,
                            "skip_tasks": vars["skip_tasks"] | self.skip_tasks,
                        },
                    )
                    for name, vars in hosts
                ],
                {},
            )
        hosts = list(dict.fromkeys(host.name for group in self.groups for host in group.hosts))
        resolved["all"] = hosts, {"binary_versions": self.binary_versions}
        return resolved
