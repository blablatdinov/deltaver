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

"""Pypi version delta."""

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
    def days(self) -> int:  # noqa: C901, WPS210, WPS231. TODO
        """Delta in days."""
        parsed_version = version.parse(self._version)
        if parsed_version.pre or parsed_version.dev:
            return 0
        sorted_versions = self._sorted_versions.fetch()
        if not sorted_versions:
            return 0
        last_version_number = version.parse(
            next(iter(list(sorted_versions[-1].keys()))),
        )
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
        for item in sorted_versions:  # noqa: WPS110, rename
            release, upload_time = next(iter(item.items()))
            if release == next_available_release:
                start = upload_time
        if not start:
            raise VersionNotFoundError
        return (datetime.datetime.now(tz=datetime.timezone.utc).date() - start).days
