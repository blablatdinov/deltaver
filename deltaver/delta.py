import datetime
from typing import Protocol, final

import attrs
from packaging.version import parse

from deltaver.exceptions import NextVersionNotFoundError
from deltaver.package import Package, VersionList


@attrs.define(frozen=True)
class Delta(Protocol):

    def days(self) -> int: pass


@final
@attrs.define(frozen=True)
class DaysDelta(Delta):

    _version: str
    _packages: VersionList
    _today: datetime.date

    def days(self) -> int:
        flag = False
        next_version_release_date = datetime.date(0, 0, 0)
        for package in self._packages.as_list():
            if flag:
                next_version_release_date = package.release_date()
                break
            if package.version() == parse(self._version):
                flag = True
        else:
            return 0
        return (self._today - next_version_release_date).days
