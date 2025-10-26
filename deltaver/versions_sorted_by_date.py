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

"""Versions sorted by date."""

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
        return sorted(
            correct_versions,
            key=self._sort_key,
        )

    def _sort_key(self, release_dict: dict[VersionNumber, UploadTime]) -> UploadTime:
        if not release_dict or not next(iter(list(release_dict.values()))):
            return datetime.date.min
        times: list[UploadTime] = list(release_dict.values())
        return next(iter(sorted(times)))
