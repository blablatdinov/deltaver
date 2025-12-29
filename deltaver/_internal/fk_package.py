# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fake package."""

import datetime
from typing import final

import attrs
from packaging.version import Version
from typing_extensions import override

from deltaver._internal.package import Package
from deltaver._internal.parsed_version import ParsedVersion


@final
@attrs.define(frozen=True)
class FkPackage(Package):
    """Fake package."""

    _name: str
    _version: str
    _release_date: datetime.date

    @override
    def version(self) -> Version:
        """Version."""
        return ParsedVersion(self._version).parse()

    @override
    def name(self) -> str:
        """Name."""
        return self._name

    @override
    def release_date(self) -> datetime.date:
        """Release date."""
        return self._release_date
