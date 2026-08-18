from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Inventory:
    @dataclass
    class Host:
        name: str
        vars: dict[str, Any] = field(default_factory=dict)
        skip_tasks: set[str] = field(default_factory=set)

    @dataclass
    class Group:
        name: str
        hosts: set[str]
        vars: dict[str, Any] = field(default_factory=dict)
        skip_tasks: set[str] = field(default_factory=set)

    vars: dict[str, Any] = field(default_factory=dict)
    skip_tasks: set[str] = field(default_factory=set)
    binary_versions: dict[str, str] = field(default_factory=dict)

    ## Internal metadata.
    _hosts: dict[str, Host] = field(default_factory=dict, init=False, repr=False)
    _groups: dict[str, Group] = field(default_factory=dict, init=False, repr=False)

    @property
    def hosts(self) -> list[Host]:
        return list(self._hosts.values())

    @hosts.setter
    def hosts(self, hosts: list[Host]):
        self._hosts.clear()
        self.add_hosts(hosts)

    @property
    def groups(self) -> list[Group]:
        return list(self._groups.values())

    @groups.setter
    def groups(self, groups: list[Group]) -> None:
        self._groups.clear()
        self.apply_groups(groups)

    def add_hosts(self, hosts: Host | list[Host]):
        if isinstance(hosts, Inventory.Host):
            hosts = [hosts]

        for host in hosts:
            if host.name in self._hosts:
                raise ValueError(f"Duplicate host name {host.name!r} in inventory.")
            self._hosts[host.name] = host

    def apply_groups(self, groups: Group | list[Group]) -> None:
        if isinstance(groups, Inventory.Group):
            groups = [groups]

        for group in groups:
            if group.name in self._groups:
                raise ValueError(f"Duplicate group name {group.name!r} in inventory.")
            for host_name in group.hosts:
                if host_name not in self._hosts:
                    raise ValueError(f"Unknown host {host_name!r} in group {group.name!r}")
            self._groups[group.name] = group

    def resolve(self) -> dict[str, tuple[list[Any], dict[str, Any]]]:
        hosts = deepcopy(self._hosts)

        for group in self.groups:
            for host_name in group.hosts:
                host = hosts[host_name]
                host.vars = {
                    **host.vars,
                    **group.vars,
                    **self._hosts[host_name].vars,
                }
                host.skip_tasks |= group.skip_tasks

        for host in hosts.values():
            host.vars = {**self.vars, **host.vars}
            host.skip_tasks |= self.skip_tasks

        resolved = {
            "all": (
                [(host.name, {**host.vars, "skip_tasks": host.skip_tasks}) for host in hosts.values()],
                {"binary_versions": self.binary_versions},
            )
        }
        for group in self.groups:
            resolved[group.name] = list(group.hosts)
        return resolved
