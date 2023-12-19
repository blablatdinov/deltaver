import attrs

from typing import Protocol


class VersionDelta(Protocol):
    
    def days(self) -> int:
        pass


@attrs.define(frozen=True)
class PypiVersionDelta(VersionDelta):

    _package_name: str
    _version: str

    def days(self):
        return 1
