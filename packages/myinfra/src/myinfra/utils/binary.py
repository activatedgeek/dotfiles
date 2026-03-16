from dataclasses import dataclass, field
from typing import ClassVar, Literal

import requests

Arch = Literal["amd64", "arm64"]


@dataclass
class Binary:
    arch: Arch
    """Architecture for the pre-compiled binary."""

    version: ClassVar[str]
    """Version of the binary."""

    use_latest: bool = field(default=False)
    """Check whether the specified version is the latest."""

    gh_repo: ClassVar[str | None] = field(default=None)
    """GitHub <username>/<repo>."""

    assets_url: ClassVar[str | None] = field(default=None)
    """URL prefix to download the assets."""

    def __post_init__(self):
        if self.arch not in self.asset_map:
            raise ValueError(f"Unsupported arch {self.arch}")

        if self.use_latest:
            latest_version = self.latest
            if latest_version is not None and latest_version != self.version:
                raise ValueError(f"Found updated version {latest_version} (!= {self.version}).")

        if self.gh_repo:
            self.assets_url = f"https://github.com/{self.gh_repo}/releases/download"

        if self.assets_url is None:
            raise ValueError("assets_url cannot be none.")

    @property
    def latest(self):
        if self.gh_repo:
            return self.gh_latest_release()

    @property
    def asset_map(self) -> dict[Arch, dict[Literal["name", "sha256sum"], str]]:
        """Map of the asset name and corresponding sha256sum."""
        raise NotImplementedError

    @property
    def src(self) -> str:
        return f"{self.assets_url}/{self.version}/{self.asset_map[self.arch]['name']}"

    @property
    def sha256sum(self) -> str:
        return self.asset_map[self.arch]["sha256sum"]

    def gh_latest_release(self) -> str:
        if not self.gh_repo:
            raise ValueError("gh_repo must be set to use _github_release")

        response = requests.get(f"https://api.github.com/repos/{self.gh_repo}/releases/latest", timeout=10)
        response.raise_for_status()
        return response.json()["tag_name"].strip()
