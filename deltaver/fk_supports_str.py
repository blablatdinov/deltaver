"""Module for foreign key supports string implementation."""

from typing import final

import attrs

from deltaver.supports_str import SupportsStr


@final
@attrs.define(frozen=True)
class FkSupportsStr(SupportsStr):
    """Fk supports str."""

    _origin: str

    def __str__(self) -> str:
        """Return the version as a string."""
        return self._origin
