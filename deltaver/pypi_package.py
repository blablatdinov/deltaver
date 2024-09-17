import datetime
from typing import final

import attrs
import httpx
from contextlib import suppress
from packaging import version

from deltaver.package import Package


class LastVersionError(Exception): ...


class SortedVersions:

    def fetch(self, name: str):
        response = httpx.get(
            httpx.URL('https://pypi.org/pypi/{0}/json'.format(self._name)),
        )
        response.raise_for_status()
        versions = list(response.json()['releases'].items())
        release_versions = []
        flag = False
        for version_number, release_info in versions:
            with suppress(version.InvalidVersion, IndexError):
                parsed_version_number = version.parse(version_number)
                if not parsed_version_number.pre and not parsed_version_number.dev:
                    release_versions.append({
                        version_number: datetime.datetime.strptime(
                            release_info[0]['upload_time'], '%Y-%m-%dT%H:%M:%S',
                        ).astimezone(datetime.timezone.utc).date()
                    })
        return sorted(
            release_versions,
            key=lambda release_dict: version.parse(next(iter(release_dict.keys()))),
        )


@final
@attrs.define(frozen=True)
class PypiPackage(Package):

    _name: str
    _version: str

    def next(self) -> Package:
        v = version.parse(self._version)
        if v.pre or v.dev:
            raise NotReleaseVersionError
        sorted_release_version = SortedVersions().fetch(self._name)
        flag = False
        for elem in sorted_release_version:
            version_number, upload_date = next(iter(elem.items()))
            if flag:
                return PypiPackage(self._name, version_number)
            if self._version == version_number:
                flag = True
        raise LastVersionError

    def release_date(self) -> datetime.date:
        sorted_release_version = SortedVersions().fetch(self._name)
        for elem in sorted_release_version:
            version_number, upload_date = next(iter(elem.items()))
            if self._version == version_number:
                return upload_date
        raise LastVersionError
