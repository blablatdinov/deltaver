import datetime
from typing import final

import attrs
from packaging import version
from typing_extensions import override

from deltaver.exceptions import TargetGreaterLastError, VersionNotFoundError
from deltaver.sorted_versions import SortedVersions
from deltaver.version_delta import VersionDelta


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
