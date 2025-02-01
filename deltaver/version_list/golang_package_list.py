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
from typing_extensions import override

from deltaver.fk_package import FkPackage
from deltaver.package import Package
from deltaver.version_list import VersionList


@final
@attrs.define(frozen=True)
class GolangPackageList(VersionList):
    """Golang package list."""

    _name: str

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        response = httpx.get('https://proxy.golang.org/{0}/@v/list'.format(self._name))
        response.raise_for_status()
        versions = response.text.splitlines()
        versions = sorted(
            versions,
            key=lambda ver: version_parse(ver[1:]),
        )
        packages = []
        for version in versions:
            response = httpx.get('https://proxy.golang.org/{0}/@v/{1}.info'.format(self._name, version))
            if response.status_code == httpx.codes.NOT_FOUND:
                # Request to get the list of versions for the module:
                # https://proxy.golang.org/github.com/russross/blackfriday/v2/@v/list
                # Response:
                # v2.0.0
                # v2.1.0-pre.1
                # v2.1.0
                # v2.0.1
                #
                # However, attempting to request information for a specific version, such as:
                # https://proxy.golang.org/github.com/russross/blackfriday/v2/@v/v2.0.0.info
                # will result in a 404 error (page not found).
                continue
            response.raise_for_status()
            packages.append(FkPackage(
                self._name,
                version,
                (
                    datetime.datetime
                    .strptime(
                        response.json()['Time'],
                        '%Y-%m-%dT%H:%M:%S%z',
                    )
                    .date()
                ),
            ))
        return packages
