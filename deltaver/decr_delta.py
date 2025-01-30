import datetime
from typing import final

import attrs
from typing_extensions import override

from deltaver.version_delta import VersionDelta


@final
@attrs.define(frozen=True)
class DecrDelta(VersionDelta):
    """Decrement delta."""

    _origin: VersionDelta
    _for_date: datetime.date

    @override
    def days(self) -> int:
        """Delta in days."""
        today = datetime.datetime.now(tz=datetime.timezone.utc).date()
        recalculated_days = self._origin.days() - (today - self._for_date).days
        return 0 if recalculated_days < 0 else recalculated_days
