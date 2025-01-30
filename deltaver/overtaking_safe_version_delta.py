from typing import final

import attrs
from typing_extensions import override

from deltaver.exceptions import TargetGreaterLastError
from deltaver.version_delta import VersionDelta


@final
@attrs.define(frozen=True)
class OvertakingSafeVersionDelta(VersionDelta):
    """Overtaking safe version delta."""

    _origin: VersionDelta
    _enable: bool

    @override
    def days(self) -> int:
        """Delta in days."""
        try:
            return self._origin.days()
        except TargetGreaterLastError:
            return 0
