# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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

from deltaver._internal.fk_package import FkPackage
from deltaver._internal.package import Package
from deltaver._internal.version_list import VersionList


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
        releases = response.json().get('releases', [])
        packages = []
        for release in releases:
            version_num = release.get('version')
            if not version_num:
                continue
            with suppress(InvalidVersion):
                version_parse(version_num)
                packages.append(FkPackage(
                    self._name,
                    version_num,
                    datetime.datetime.strptime(release.get('inserted_at', ''), '%Y-%m-%dT%H:%M:%S.%f%z').date(),
                ))
        return packages
