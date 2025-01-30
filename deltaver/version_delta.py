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

import datetime
import json
from contextlib import suppress
from pathlib import Path
from typing import Protocol, final

import attrs
import httpx
from packaging import version
from typing_extensions import TypeAlias, override

from deltaver.exceptions import TargetGreaterLastError, VersionNotFoundError

VersionNumber: TypeAlias = str
UploadTime: TypeAlias = datetime.date
SortedVersionsList: TypeAlias = list[dict[VersionNumber, UploadTime]]


class VersionDelta(Protocol):
    """Version delta protocol."""

    def days(self) -> int:
        """Delta in days."""


class SortedVersions(Protocol):
    """Sorted versions protocol."""

    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""


@final
@attrs.define(frozen=True)
class FkSortedVersions(SortedVersions):
    """Fake sorted versions."""

    _value: SortedVersionsList

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        return self._value


@final
@attrs.define(frozen=True)
class FkVersionDelta(VersionDelta):
    """Fake version delta."""

    _value: int

    @override
    def days(self) -> int:
        """Delta in days."""
        return self._value


@final
@attrs.define(frozen=True)
class VersionsSortedByDate(SortedVersions):
    """Versions sorted by date."""

    _package_name: str

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._package_name))
        response.raise_for_status()
        versions = list(response.json()['releases'].items())
        correct_versions = []
        for version_number, release_info in versions:
            with suppress(version.InvalidVersion, IndexError):
                if not version.parse(version_number).pre:
                    correct_versions.append({
                        version_number: datetime.datetime.strptime(
                            release_info[0]['upload_time'], '%Y-%m-%dT%H:%M:%S',
                        ).astimezone(datetime.timezone.utc).date(),
                    })
        def _sort_key(release_dict: dict[VersionNumber, UploadTime]) -> datetime.date:
            if not release_dict or not next(iter(list(release_dict.values()))):
                return datetime.date(1, 1, 1)
            times: list[UploadTime] = list(release_dict.values())
            return next(iter(sorted(times)))
        return sorted(
            correct_versions,
            key=_sort_key,
        )


@final
@attrs.define(frozen=True)
class CachedSortedVersions(SortedVersions):
    """Cached sorted versions."""

    _origin: SortedVersions
    _package_name: str

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        cache_dir = Path('.deltaver_cache')
        (cache_dir / self._package_name).mkdir(exist_ok=True, parents=True)
        if cache_dir.exists():
            for x in cache_dir.glob('**/*.json'):
                if x.name != '{0}.json'.format(datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d')):
                    x.unlink()
        cache_path = cache_dir / self._package_name / '{0}.json'.format(
            datetime.datetime.now(tz=datetime.timezone.utc).date(),
        )
        if cache_path.exists():
            return [
                {
                    next(iter(elem.keys())): datetime.datetime.strptime(
                        next(iter(elem.values())),
                        '%Y-%m-%dT%H:%M:%S',
                    ).astimezone(datetime.timezone.utc).date(),
                }
                for elem  in json.loads(cache_path.read_text())
            ]
        origin_val = self._origin.fetch()
        cache_path.write_text(json.dumps([
            {next(iter(dict_.keys())): next(iter(dict_.values())).strftime('%Y-%m-%dT%H:%M:%S')}
            for dict_ in origin_val
        ]))
        return origin_val


@final
@attrs.define(frozen=True)
class PypiVersionsSortedBySemver(SortedVersions):
    """Pypi versions sorted by semver."""

    _artifactory_domain: str
    _package_name: str

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        response = httpx.get(
            httpx.URL(self._artifactory_domain).join('pypi/{0}/json'.format(self._package_name)),
        )
        response.raise_for_status()
        versions = list(response.json()['releases'].items())
        correct_versions = []
        for version_number, release_info in versions:
            with suppress(version.InvalidVersion, IndexError):
                v = version.parse(version_number)
                if not v.pre and not v.dev:
                    correct_versions.append({
                        version_number: datetime.datetime.strptime(
                            release_info[0]['upload_time'], '%Y-%m-%dT%H:%M:%S',
                        ).astimezone(datetime.timezone.utc).date(),
                    })
        return sorted(
            correct_versions,
            key=lambda release_dict: version.parse(next(iter(release_dict.keys()))),
        )


@final
@attrs.define(frozen=True)
class NpmjsVersionsSortedBySemver(SortedVersions):
    """Npmjs versions sorted by semver."""

    _artifactory_domain: str
    _package_name: str

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        response = httpx.get(
            httpx.URL(self._artifactory_domain).join(self._package_name),
        )
        response.raise_for_status()
        versions = response.json()['time'].items()
        correct_versions = []
        for version_number, release_time in versions:
            with suppress(version.InvalidVersion, IndexError, KeyError):
                parsed_version = version.parse(version_number)
                if not parsed_version.is_prerelease and not parsed_version.is_devrelease:
                    parsed_release_time = datetime.datetime.strptime(
                        release_time, '%Y-%m-%dT%H:%M:%S.%f%z',
                    ).astimezone(datetime.timezone.utc).date()
                    correct_versions.append({
                        version_number: parsed_release_time,
                    })
        return sorted(
            correct_versions,
            key=lambda release_dict: version.parse(next(iter(release_dict.keys()))),
        )


@final
@attrs.define(frozen=True)
class OvertakingSafeVersionDelta(VersionDelta):
    """Overtaking safe version delta."""

    _origin: VersionDelta
    _enable: bool

    @override
    def days(self) -> int:
        """Delta in days."""
        try:
            return self._origin.days()
        except TargetGreaterLastError:
            return 0


@final
@attrs.define(frozen=True)
class PypiVersionDelta(VersionDelta):
    """Pypi version delta."""

    _sorted_versions: SortedVersions
    _version: str

    @override
    def days(self) -> int:  # noqa: C901. TODO
        """Delta in days."""
        v = version.parse(self._version)
        if v.pre or v.dev:
            return 0
        sorted_versions = self._sorted_versions.fetch()
        if not sorted_versions:
            return 0
        last_version_number = version.parse(next(iter(list(sorted_versions[-1].keys()))))
        if version.parse(self._version) > last_version_number:
            raise TargetGreaterLastError
        if next(iter(sorted_versions[-1].keys())) == self._version:
            return 0
        start = None
        next_available_release = None
        flag = False
        for release_info in sorted_versions:
            release_number = next(iter(release_info.keys()))
            if flag:
                next_available_release = release_number
                break
            if release_number == self._version:
                flag = True
        for item in sorted_versions:
            release, upload_time = next(iter(item.items()))
            if release == next_available_release:
                start = upload_time
        if not start:
            raise VersionNotFoundError
        return (datetime.datetime.now(tz=datetime.timezone.utc).date() - start).days


@final
@attrs.define(frozen=True)
class DecrDelta(VersionDelta):
    """Decrement delta."""

    _origin: VersionDelta
    _for_date: datetime.date

    @override
    def days(self) -> int:
        """Delta in days."""
        today = datetime.datetime.now(tz=datetime.timezone.utc).date()
        recalculated_days = self._origin.days() - (today - self._for_date).days
        return 0 if recalculated_days < 0 else recalculated_days

