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

"""Pypi package list."""

import datetime
from typing import final

import attrs
import httpx
import pytz
from packaging.version import Version
from typing_extensions import override

from deltaver.package import Package
from deltaver.parsed_version import ParsedVersion
from deltaver.version_list import VersionList


@final
@attrs.define(frozen=True)
class PypiPackage(Package):
    """Pypi package list."""

    _name: str
    _version: str
    _version_list: VersionList

    @override
    def version(self) -> Version:
        """Version."""
        return ParsedVersion(self._version).parse()

    @override
    def name(self) -> str:
        """Name."""
        return self._name

    @override
    def release_date(self) -> datetime.date:
        """Release date."""
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._name))
        releases = {
            str(ParsedVersion(v).parse()): info
            for v, info in response.json()['releases'].items()
        }
        response.raise_for_status()
        return datetime.datetime.strptime(
            releases[str(self.version())][0]['upload_time'],
            '%Y-%m-%dT%H:%M:%S',
        ).astimezone(pytz.UTC).date()
