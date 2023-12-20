import datetime

import attrs
import httpx
from packaging import version

from typing import Protocol


class VersionNotFoundError(Exception):
    pass


class VersionDelta(Protocol):
    
    def days(self) -> int:
        pass


@attrs.define(frozen=True)
class PypiVersionDelta(VersionDelta):

    _package_name: str
    _version: str

    def days(self):
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._package_name))
        response.raise_for_status()
        available_release_versions = sorted(
            [
                {version_number: release_info}
                for version_number, release_info in response.json()['releases'].items()
                if not version.parse(version_number).pre
            ],
            key=lambda release_dict: version.parse(list(release_dict.keys())[0]),
        )
        if list(available_release_versions[-1].keys())[0] == self._version:
            return 0
        start = None
        next_available_release = None
        flag = False
        for release_number, _ in response.json()['releases'].items():
            if flag:
                next_available_release = release_number
                break
            if release_number == self._version:
                flag = True
        for version_info, release in response.json()['releases'].items():
            if release == []:
                continue
            upload_time = datetime.datetime.strptime(release[0]['upload_time'], '%Y-%m-%dT%H:%M:%S').date()
            if version_info == next_available_release:
                start = upload_time
        if not start:
            raise VersionNotFoundError
        return (datetime.datetime.now().date() - start).days
