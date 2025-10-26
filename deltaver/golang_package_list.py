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

import asyncio
import datetime
from collections.abc import Sequence
from typing import final

import attrs
import httpx
from typing_extensions import override

from deltaver.fk_package import FkPackage
from deltaver.package import Package
from deltaver.parsed_version import ParsedVersion
from deltaver.version_list import VersionList


@final
@attrs.define(frozen=True)
class GolangPackageList(VersionList):
    """Golang package list."""

    _name: str

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        return asyncio.run(self._async_as_list())

    async def _async_as_list(self) -> Sequence[Package]:
        """Async list representation with parallel requests."""
        async with httpx.AsyncClient() as client:
            response = await client.get('https://proxy.golang.org/{0}/@v/list'.format(self._name))
            response.raise_for_status()
            versions = [
                ParsedVersion(ver)
                for ver in response.text.splitlines()
            ]
            versions = sorted(
                [ver for ver in versions if ver.valid()],
                key=lambda ver: ver.parse(),
            )
            tasks = []
            for version in versions:
                url = 'https://proxy.golang.org/{0}/@v/{1}.info'.format(self._name, version.origin())
                task = self._fetch_version_info(client, url, version)
                tasks.append(task)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            packages = []
            for result in results:
                if isinstance(result, Exception):
                    continue
                if result is not None:
                    packages.append(result)
            return [p for p in packages if not isinstance(p, BaseException)]

    async def _fetch_version_info(
        self,
        client: httpx.AsyncClient,
        url: str,
        version: ParsedVersion,
    ) -> Package | None:
        """Fetch version info for a single version."""
        try:
            return await self._inner(client, url, version)
        except httpx.HTTPError:
            return None

    async def _inner(self, client, url, version):
        response = await client.get(url)
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
            return None
        response.raise_for_status()
        return FkPackage(
            self._name,
            version.origin(),
            (
                datetime.datetime
                .strptime(
                    response.json()['Time'],
                    '%Y-%m-%dT%H:%M:%S%z',
                )
                .date()
            ),
        )
