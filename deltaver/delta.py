import datetime
from typing import Protocol, final

import attrs

from deltaver.exceptions import NextVersionNotFoundError
from deltaver.package import Package


@attrs.define(frozen=True)
class Delta(Protocol):

    def days(self) -> int: pass


@final
@attrs.define(frozen=True)
class DaysDelta(Delta):

    _package: Package
    _today: datetime.date

    def days(self) -> int:
        try:
            next_version_package = self._package.next()
        except NextVersionNotFoundError:
            return 0
        return (self._today - next_version_package.release_date()).days
