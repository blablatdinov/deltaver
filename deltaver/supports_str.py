"""Module for supports string protocol."""

from typing import Protocol


class SupportsStr(Protocol):
    """Supports str."""

    def __str__(self) -> str:
        """Return the version as a string."""
