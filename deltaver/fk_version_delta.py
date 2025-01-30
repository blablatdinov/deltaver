from typing import final

import attrs
from typing_extensions import override

from deltaver.version_delta import VersionDelta


@final
@attrs.define(frozen=True)
class FkVersionDelta(VersionDelta):
    """Fake version delta."""

    _value: int

    @override
    def days(self) -> int:
        """Delta in days."""
        return self._value
