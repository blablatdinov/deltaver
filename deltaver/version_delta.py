import datetime
from contextlib import suppress
from typing import Protocol, final

import attrs
import httpx
from packaging import version


@final
class VersionNotFoundError(Exception):
    pass


class VersionDelta(Protocol):

    def days(self) -> int: ...


@attrs.define(frozen=True)
@final
class PypiVersionDelta(VersionDelta):

    _package_name: str
    _version: str

    def days(self) -> int:
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._package_name))
        response.raise_for_status()
        versions = [
            (version_number, release_info)
            for version_number, release_info in response.json()['releases'].items()
        ]
        correct_versions = []
        for version_number, release_info in versions:
            with suppress(version.InvalidVersion):
                if not version.parse(version_number).pre:
                    correct_versions.append({
                        version_number: release_info,
                    })
        available_release_versions = sorted(
            correct_versions,
            key=lambda release_dict: version.parse(next(iter(release_dict.keys()))),
        )
        if not available_release_versions:
            return 0
        if next(iter(available_release_versions[-1].keys())) == self._version:
            return 0
        start = None
        next_available_release = None
        flag = False
        for release_number in response.json()['releases']:
            if flag:
                next_available_release = release_number
                break
            if release_number == self._version:
                flag = True
        for version_info, release in response.json()['releases'].items():
            if release == []:
                continue
            upload_time = datetime.datetime.strptime(
                release[0]['upload_time'], '%Y-%m-%dT%H:%M:%S',
            ).astimezone(datetime.timezone.utc).date()
            if version_info == next_available_release:
                start = upload_time
        if not start:
            raise VersionNotFoundError
        return (datetime.datetime.now(tz=datetime.timezone.utc).date() - start).days
