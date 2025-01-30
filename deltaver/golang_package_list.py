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

"""Golang package list."""

import datetime
from collections.abc import Sequence
from typing import final

import attrs
import httpx

from packaging.version import parse as version_parse
from deltaver.fk_package import FkPackage
from deltaver.package import Package
from deltaver.version_list import VersionList


@final
@attrs.define(frozen=True)
class GolangPackageList(VersionList):
    """Golang package list."""

    _name: str

    def as_list(self) -> Sequence[Package]:
        """List representation."""
        response = httpx.get('https://proxy.golang.org/{0}/@v/list'.format(self._name))
        response.raise_for_status()
        versions = response.text.splitlines()
        versions = sorted(
            versions,
            key=lambda v: version_parse(v[1:]),
        )
        packages = []
        for version in versions:
            response = httpx.get('https://proxy.golang.org/{0}/@v/{1}.info'.format(self._name, version))
            response.raise_for_status()
            packages.append(FkPackage(
                self._name,
                version,
                datetime.datetime.strptime(
                    response.json()['Time'],
                    '%Y-%m-%dT%H:%M:%SZ',
                ),
            ))
        return packages
