# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Pypi package list."""

import datetime
from typing import final

import attrs
import httpx
import pytz
from packaging.version import Version
from typing_extensions import override

from deltaver._internal.package import Package
from deltaver._internal.parsed_version import ParsedVersion
from deltaver._internal.version_list import VersionList


@final
@attrs.define(frozen=True)
class PypiPackage(Package):
    """Pypi package list."""

    _name: str
    _version: str
    _version_list: VersionList

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
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._name))
        releases = {
            str(ParsedVersion(ver).parse()): pkg_info
            for ver, pkg_info in response.json()['releases'].items()
        }
        response.raise_for_status()
        return datetime.datetime.strptime(
            releases[str(self.version())][0]['upload_time'],
            '%Y-%m-%dT%H:%M:%S',
        ).astimezone(pytz.UTC).date()
