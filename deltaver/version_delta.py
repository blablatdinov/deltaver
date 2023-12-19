import attrs

from typing import Protocol


class VersionDelta(Protocol):
    
    def days(self) -> int:
        pass


@attrs.define(frozen=True)
class PypiVersionDelta(VersionDelta):

    def days(self):
        return 1
