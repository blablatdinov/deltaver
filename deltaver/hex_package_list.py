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

"""Hex package list."""

import datetime
from collections.abc import Sequence
from contextlib import suppress
from typing import final

import attrs
import httpx
from packaging.version import InvalidVersion
from packaging.version import parse as version_parse
from typing_extensions import override

from deltaver.package import Package
from deltaver.hex_package import HexPackage
from deltaver.version_list import VersionList
from deltaver.fk_package import FkPackage


@final
@attrs.define(frozen=True)
class HexPackageList(VersionList):
    """Hex package list."""

    _name: str

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        response = httpx.get('https://hex.pm/api/packages/{0}'.format(self._name))
        response.raise_for_status()
        packages = []
        package_data = response.json()
        releases = package_data.get('releases', [])
        for release in releases:
            version_num = release.get('version')
            if not version_num:
                continue
            with suppress(InvalidVersion):
                version_parse(version_num)
                inserted_at = release.get('inserted_at', '')
                release_date = datetime.datetime.strptime(inserted_at, '%Y-%m-%dT%H:%M:%S.%fZ').date()
                packages.append(FkPackage(
                    self._name,
                    version_num,
                    release_date,
                ))
        return packages
