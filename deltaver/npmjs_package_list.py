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

"""Npmjs package list."""

import datetime
from collections.abc import Sequence
from contextlib import suppress
from typing import final

import attrs
import httpx
from packaging.version import InvalidVersion
from typing_extensions import override

from deltaver.fk_package import FkPackage
from deltaver.package import Package
from deltaver.parsed_version import ParsedVersion
from deltaver.version_list import VersionList


@final
@attrs.define(frozen=True)
class NpmjsPackageList(VersionList):
    """Npmjs package list."""

    _name: str

    @override
    def as_list(self) -> Sequence[Package]:  # noqa: WPS210. TODO: minimize variables
        """List representation."""
        response = httpx.get(httpx.URL('https://registry.npmjs.org').join(self._name))
        response.raise_for_status()
        versions = response.json()['time'].items()
        correct_versions = []
        for version_number, release_time in versions:
            # Skip non-version keys like 'created', 'modified', etc.
            if version_number in ['created', 'modified', 'unpublished']:
                continue
            with suppress(InvalidVersion, IndexError, KeyError):
                parsed_version = ParsedVersion(version_number).parse()
                if not parsed_version.is_prerelease:
                    parsed_release_time = (
                        datetime.datetime.strptime(
                            release_time,
                            '%Y-%m-%dT%H:%M:%S.%f%z',
                        )
                        .astimezone(datetime.timezone.utc)
                        .date()
                    )
                    correct_versions.append(
                        FkPackage(
                            self._name,
                            version_number,
                            parsed_release_time,
                        ),
                    )
        return correct_versions
