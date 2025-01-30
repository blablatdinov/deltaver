import datetime
from contextlib import suppress
from typing import final

import attrs
import httpx
from packaging import version
from typing_extensions import override

from deltaver.sorted_versions import SortedVersions
from deltaver.version_delta import SortedVersionsList, UploadTime, VersionNumber


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
