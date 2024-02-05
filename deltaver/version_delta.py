import datetime
import json
from contextlib import suppress
from itertools import chain
from pathlib import Path
from typing import Protocol, final

import attrs
import httpx
from packaging import version
from typing_extensions import TypeAlias, TypedDict


class VersionInfo(TypedDict):

    upload_time: str


VersionNumber: TypeAlias = str
SortedVersionsList: TypeAlias = list[dict[VersionNumber, list[VersionInfo]]]


@final
class VersionNotFoundError(Exception):
    pass


@final
class TargetGreaterLastError(Exception):
    pass


class VersionDelta(Protocol):

    def days(self) -> int: ...


class SortedVersions(Protocol):

    def fetch(self) -> SortedVersionsList: ...


@final
@attrs.define(frozen=True)
class FkSortedVersions(SortedVersions):

    _value: SortedVersionsList

    def fetch(self) -> SortedVersionsList:
        return self._value


@final
@attrs.define(frozen=True)
class FkVersionDelta(VersionDelta):

    _value: int

    def days(self) -> int:
        return self._value


@final
@attrs.define(frozen=True)
class VersionsSortedByDate(SortedVersions):

    _package_name: str

    def fetch(self) -> SortedVersionsList:
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._package_name))
        response.raise_for_status()
        versions = list(response.json()['releases'].items())
        correct_versions = []
        for version_number, release_info in versions:
            with suppress(version.InvalidVersion):
                if not version.parse(version_number).pre:
                    correct_versions.append({
                        version_number: release_info,
                    })
        def _sort_key(release_dict: VersionInfo) -> datetime.date:
            times = []
            if not release_dict or not next(iter(list(release_dict.values()))):
                return datetime.date(1, 1, 1)
            times = [  # type: ignore[var-annotated]
                datetime.datetime.strptime(
                    dict_['upload_time'], '%Y-%m-%dT%H:%M:%S',
                ).astimezone(datetime.timezone.utc).date()
                for dict_ in chain.from_iterable(release_dict.values())  # type: ignore[arg-type]
            ]
            return next(iter(sorted(times)))
        return sorted(
            correct_versions,
            key=_sort_key,  # type: ignore[arg-type]
        )


@final
@attrs.define(frozen=True)
class CachedSortedVersions(SortedVersions):

    _origin: SortedVersions
    _package_name: str

    def fetch(self) -> SortedVersionsList:
        cache_dir = Path('.deltaver_cache')
        (cache_dir / self._package_name).mkdir(exist_ok=True, parents=True)
        if cache_dir.exists():
            [
                x.unlink()
                for x in cache_dir.glob('**/*.json')
                if x != datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d')
            ]
        cache_path = cache_dir / self._package_name / '{0}.json'.format(
            datetime.datetime.now(tz=datetime.timezone.utc).date(),
        )
        if cache_path.exists():
            return json.loads(cache_path.read_text())
        origin_val = self._origin.fetch()
        cache_path.write_text(json.dumps(origin_val))
        return origin_val


@final
@attrs.define(frozen=True)
class VersionsSortedBySemver(SortedVersions):

    _artifactory_domain: str
    _package_name: str

    def fetch(self) -> SortedVersionsList:
        response = httpx.get(
            httpx.URL(self._artifactory_domain).join('pypi/{0}/json'.format(self._package_name)),
        )
        response.raise_for_status()
        versions = list(response.json()['releases'].items())
        correct_versions = []
        for version_number, release_info in versions:
            with suppress(version.InvalidVersion):
                v = version.parse(version_number)
                if not v.pre and not v.dev:
                    correct_versions.append({
                        version_number: release_info,
                    })
        return sorted(
            correct_versions,
            key=lambda release_dict: version.parse(next(iter(release_dict.keys()))),
        )


@final
@attrs.define(frozen=True)
class OvertakingSafeVersionDelta(VersionDelta):

    _origin: VersionDelta
    _enable: bool

    def days(self) -> int:
        try:
            return self._origin.days()
        except TargetGreaterLastError:
            return 0


@final
@attrs.define(frozen=True)
class PypiVersionDelta(VersionDelta):

    _sorted_versions: SortedVersions
    _version: str

    def days(self) -> int:  # noqa: C901. TODO
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
            release = next(iter(item.keys()))
            item_values = list(chain.from_iterable(item.values()))
            if not item_values:
                continue
            upload_time = datetime.datetime.strptime(
                item_values[0]['upload_time'], '%Y-%m-%dT%H:%M:%S',
            ).astimezone(datetime.timezone.utc).date()
            if release == next_available_release:
                start = upload_time
        if not start:
            raise VersionNotFoundError
        return (datetime.datetime.now(tz=datetime.timezone.utc).date() - start).days


@final
@attrs.define(frozen=True)
class DecrDelta(VersionDelta):

    _origin: VersionDelta
    _for_date: datetime.date

    def days(self) -> int:
        today = datetime.datetime.now(tz=datetime.timezone.utc).date()
        recalculated_days = self._origin.days() - (today - self._for_date).days
        return 0 if recalculated_days < 0 else recalculated_days
