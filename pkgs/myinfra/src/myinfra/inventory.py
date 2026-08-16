from dataclasses import dataclass, field
from typing import Any


@dataclass
class InventoryHost:
    name: str
    host: str | None = None
    vars: dict[str, Any] = field(default_factory=dict)
    skip_tasks: set[str] = field(default_factory=set)

    def resolve(self) -> tuple[str, dict[str, Any]]:
        return self.name, self.vars


@dataclass
class InventoryGroup:
    name: str
    hosts: list[InventoryHost]
    vars: dict[str, Any] = field(default_factory=dict)
    skip_tasks: set[str] = field(default_factory=set)

    def resolve(self) -> tuple[list[tuple[str, dict[str, Any]]], dict[str, Any]]:
        vars = {**self.vars, "skip_tasks": self.skip_tasks}
        return [host.resolve() for host in self.hosts], vars


@dataclass
class Inventory:
    groups: list[InventoryGroup]
    vars: dict[str, Any] = field(default_factory=dict)
    skip_tasks: set[str] = field(default_factory=set)
    binary_versions: dict[str, str] = field(default_factory=dict)

    def resolve(self) -> dict[str, tuple[list[Any], dict[str, Any]]]:
        resolved = {group.name: group.resolve() for group in self.groups}
        hosts = list(dict.fromkeys(host.name for group in self.groups for host in group.hosts))
        vars = {
            **self.vars,
            "skip_tasks": self.skip_tasks,
            "binary_versions": self.binary_versions,
        }
        resolved["all"] = hosts, vars
        return resolved
