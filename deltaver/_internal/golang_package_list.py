# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Golang package list."""

import asyncio
import datetime
from collections.abc import Sequence
from typing import final

import attrs
import httpx
from typing_extensions import override

from deltaver._internal.fk_package import FkPackage
from deltaver._internal.package import Package
from deltaver._internal.parsed_version import ParsedVersion
from deltaver._internal.version_list import VersionList


@final
@attrs.define(frozen=True)
class GolangPackageList(VersionList):
    """Golang package list."""

    _name: str

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        return asyncio.run(self._async_as_list())

    async def _async_as_list(self) -> Sequence[Package]:  # noqa: WPS210
        """Async list representation with parallel requests."""
        async with httpx.AsyncClient() as client:
            response = await client.get('https://proxy.golang.org/{0}/@v/list'.format(self._name))
            response.raise_for_status()
            versions = [
                ParsedVersion(ver)
                for ver in response.text.splitlines()
            ]
            tasks = [
                self._fetch_version_info(
                    client,
                    'https://proxy.golang.org/{0}/@v/{1}.info'.format(self._name, version.origin()),
                    version,
                )
                for version in sorted(
                    [ver for ver in versions if ver.valid()],
                    key=lambda ver: ver.parse(),
                )
            ]
            packages = []
            for pkg in await asyncio.gather(*tasks, return_exceptions=True):
                if isinstance(pkg, BaseException):
                    continue
                if pkg is not None:
                    packages.append(pkg)
            return packages

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

    async def _inner(self, client: httpx.AsyncClient, url: str, version: ParsedVersion) -> Package | None:
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
