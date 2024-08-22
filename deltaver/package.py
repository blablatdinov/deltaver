from __future__ import annotations

import datetime
import string
from contextlib import suppress
from typing import Protocol, final

import attrs
import httpx
from packaging.version import InvalidVersion, Version, parse

from deltaver.exceptions import NextVersionNotFoundError


class Package(Protocol):

    def version(self) -> Version: pass
    def name(self) -> str: pass
    def release_date(self) -> datetime.datetime: pass


class VersionList(Protocol):

    def as_list(self) -> list[Package]: pass


@final
@attrs.define(frozen=True)
class FkVersionList(VersionList):

    _packages: list[Package]

    def as_list(self) -> list[Package]:
        return self._packages


@final
@attrs.define(frozen=True)
class FkVersionList(VersionList):

    _origin: list[Package]

    def as_list(self) -> list[Package]:
        return self._origin


@final
@attrs.define(frozen=True)
class FkPackage(Package):

    _name: str
    _version: str
    _release_date: datetime.date

    def version(self) -> Version:
        return parse(self._version)

    def name(self) -> str:
        return self._name

    def release_date(self) -> datetime.datetime:
        return self._release_date


class PackageInfo(Protocol):

    def content(self) -> dict: pass


@final
@attrs.define(frozen=True)
class PypiPackageList(VersionList):

    _name: str

    def as_list(self) -> list[Package]:
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

    _origin: VersionList
    _cache_value: list
    _cached: bool

    @classmethod
    def ctor(cls, origin):
        return cls(origin, [], False)

    def as_list(self) -> list[Package]:
        if self._cached:
            return self._cache_value
        self._cache_value = self._origin.as_list()
        return self._cache_value

@final
@attrs.define(frozen=True)
class FilteredPackageList(VersionList):

    _origin: VersionList

    def as_list(self) -> list[Package]:
        packages = []
        for package in self._origin.as_list():
            if set(string.ascii_letters).intersection(str(package.version())):
                continue
            packages.append(package)
        return packages


@final
@attrs.define(frozen=True)
class SortedPackageList(VersionList):

    _origin: VersionList

    def as_list(self) -> list[Package]:
        return sorted(
            self._origin.as_list(),
            key=lambda pkg: pkg.version(),
        )


@final
@attrs.define(frozen=True)
class PypiPackage(Package):

    _name: str
    _version: str
    _version_list: VersionList

    def version(self) -> Version:
        return parse(self._version)

    def name(self) -> str:
        return self._name

    def release_date(self) -> datetime.date:
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._name))
        response.raise_for_status()
        return datetime.datetime.strptime(
            response.json()['releases'][str(self.version())][0]['upload_time'],
            '%Y-%m-%dT%H:%M:%S',
        ).date()

