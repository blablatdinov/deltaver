from typing import final

import attrs
from typing_extensions import override

from deltaver.sorted_versions import SortedVersions
from deltaver.version_delta import SortedVersionsList


@final
@attrs.define(frozen=True)
class FkSortedVersions(SortedVersions):
    """Fake sorted versions."""

    _value: SortedVersionsList

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        return self._value
