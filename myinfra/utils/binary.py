from dataclasses import dataclass
from typing import ClassVar, Dict


@dataclass
class Binary:
    arch: str
    version: ClassVar[str]

    def __post_init__(self):
        if self.arch not in self._arch_map:
            raise ValueError(f"Unsupported arch {self.arch}")

    @property
    def _arch_map(self) -> Dict[str, Dict[str, str]]:
        raise NotImplementedError

    @property
    def src(self) -> str:
        return self._arch_map[self.arch]["src"]

    @property
    def sha256sum(self) -> str:
        return self._arch_map[self.arch]["sha256sum"]
