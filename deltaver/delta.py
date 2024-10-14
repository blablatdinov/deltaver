# The MIT License (MIT).
#
# Copyright (c) 2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Delta."""

import datetime
from typing import Protocol, final

import attrs
from packaging.version import parse as version_parse

from deltaver.package import VersionList


@attrs.define(frozen=True)
class Delta(Protocol):
    """Delta."""

    def days(self) -> int:
        """Days of delta."""


@final
@attrs.define(frozen=True)
class DaysDelta(Delta):
    """Delta."""

    _version: str
    _packages: VersionList
    _today: datetime.date

    def days(self) -> int:
        """Days of delta."""
        flag = False
        next_version_release_date = datetime.date(1, 1, 1)
        for package in self._packages.as_list():
            if flag:
                next_version_release_date = package.release_date()
                break
            if package.version() == version_parse(self._version):
                flag = True
        else:
            return 0
        return (self._today - next_version_release_date).days
