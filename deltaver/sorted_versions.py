from typing import Protocol

from deltaver.version_delta import SortedVersionsList


class SortedVersions(Protocol):
    """Sorted versions protocol."""

    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
