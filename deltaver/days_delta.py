# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Days delta."""

import datetime
from typing import final

import attrs
from rich import print as rich_print
from typing_extensions import override

from deltaver.delta import Delta
from deltaver.exceptions import InvalidVersionError
from deltaver.parsed_version import ParsedVersion
from deltaver.version_list import VersionList


@final
@attrs.define(frozen=True)
class DaysDelta(Delta):
    """Days delta."""

    _version: str
    _packages: VersionList
    _today: datetime.date

    @override
    def days(self) -> int:
        """Days of delta."""
        flag = False
        next_version_release_date = datetime.date.min
        try:
            target_version = ParsedVersion(self._version).parse()
        except InvalidVersionError:
            rich_print(f'[yellow]Version {self._version} can not been parsed')
            return 0
        for package in self._packages.as_list():
            if flag:
                next_version_release_date = package.release_date()
                break
            if package.version() == target_version:
                flag = True
        else:
            return 0
        return (self._today - next_version_release_date).days
