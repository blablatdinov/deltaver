# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Pypi package list."""

import datetime
from collections.abc import Sequence
from contextlib import suppress
from typing import final

import attrs
import httpx
from typing_extensions import override

from deltaver._internal.exceptions import InvalidVersionError
from deltaver._internal.fk_package import FkPackage
from deltaver._internal.package import Package
from deltaver._internal.parsed_version import ParsedVersion
from deltaver._internal.version_list import VersionList


@final
@attrs.define(frozen=True)
class PypiPackageList(VersionList):
    """Pypi package list."""

    _name: str

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        response = httpx.get('https://pypi.org/pypi/{0}/json'.format(self._name))
        response.raise_for_status()
        packages = []
        for version_num, release_info in response.json()['releases'].items():
            if not release_info or release_info[0]['yanked']:
                continue
            with suppress(InvalidVersionError):
                ParsedVersion(version_num).parse()
                packages.append(FkPackage(
                    self._name,
                    version_num,
                    (
                        datetime.datetime
                        .strptime(release_info[0]['upload_time'], '%Y-%m-%dT%H:%M:%S')
                        .astimezone(tz=datetime.timezone.utc)
                        .date()
                    ),
                ))
        return packages
