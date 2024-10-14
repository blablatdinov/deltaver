# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Package."""

from __future__ import annotations

import datetime
import string
from contextlib import suppress
from typing import Protocol, final

import attrs
import httpx
import pytz
from packaging.version import InvalidVersion, Version, parse


class Package(Protocol):
    """Package."""

    def version(self) -> Version:
        """Version."""

    def name(self) -> str:
        """Name."""

    def release_date(self) -> datetime.datetime:
        """Release date."""


class VersionList(Protocol):
    """Version list."""

    def as_list(self) -> list[Package]:
        """List representation."""


@final
@attrs.define(frozen=True)
class FkVersionList(VersionList):
    """Fake version list."""

    _packages: list[Package]

    def as_list(self) -> list[Package]:
        """List representation."""
        return self._packages


@final
@attrs.define(frozen=True)
class FkPackage(Package):
    """Fake package."""

    _name: str
    _version: str
    _release_date: datetime.date

    def version(self) -> Version:
        """Version."""
        return parse(self._version)

    def name(self) -> str:
        """Name."""
        return self._name

    def release_date(self) -> datetime.datetime:
        """Release date."""
        return self._release_date


class PackageInfo(Protocol):
    """Package info."""

    def content(self) -> dict:  # FIXME
        """Content."""


@final
@attrs.define(frozen=True)
class PypiPackageList(VersionList):
    """Pypi package list."""

    _name: str

    def as_list(self) -> list[Package]:
        """List representation."""
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._name))
        response.raise_for_status()
        packages = []
        for version_num, release_info in response.json()['releases'].items():
            if not release_info:
                continue
            with suppress(InvalidVersion):
                parse(version_num)
                packages.append(PypiPackage(
                    self._name,
                    version_num,
                    self,
                ))
        return packages


@final
@attrs.define
class CachedPackageList(VersionList):
    """Cached packages list."""

    _origin: VersionList
    _cache_value: list
    _cached: bool

    @classmethod
    def ctor(cls, origin: VersionList) -> VersionList:
        """Ctor."""
        return cls(origin, [], cached=False)

    def as_list(self) -> list[Package]:
        """List representation."""
        if self._cached:
            return self._cache_value
        self._cache_value = self._origin.as_list()
        return self._cache_value

@final
@attrs.define(frozen=True)
class FilteredPackageList(VersionList):
    """Filtered packages list."""

    _origin: VersionList

    def as_list(self) -> list[Package]:
        """List representation."""
        packages = []
        for package in self._origin.as_list():
            if set(string.ascii_letters).intersection(str(package.version())):
                continue
            packages.append(package)
        return packages


@final
@attrs.define(frozen=True)
class SortedPackageList(VersionList):
    """Sorted package list."""

    _origin: VersionList

    def as_list(self) -> list[Package]:
        """List representation."""
        return sorted(
            self._origin.as_list(),
            key=lambda pkg: pkg.version(),
        )


@final
@attrs.define(frozen=True)
class PypiPackage(Package):
    """Pypi package list."""

    _name: str
    _version: str
    _version_list: VersionList

    def version(self) -> Version:
        """Version."""
        return parse(self._version)

    def name(self) -> str:
        """Name."""
        return self._name

    def release_date(self) -> datetime.date:
        """Release date."""
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._name))
        response.raise_for_status()
        return datetime.datetime.strptime(
            response.json()['releases'][str(self.version())][0]['upload_time'],
            '%Y-%m-%dT%H:%M:%S',
        ).astimezone(pytz.UTC).date()
