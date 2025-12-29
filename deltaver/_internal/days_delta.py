# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Days delta."""

import datetime
from typing import final

import attrs
from rich import print as rich_print
from typing_extensions import override

from deltaver._internal.delta import Delta
from deltaver._internal.exceptions import InvalidVersionError
from deltaver._internal.parsed_version import ParsedVersion
from deltaver._internal.version_list import VersionList


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
