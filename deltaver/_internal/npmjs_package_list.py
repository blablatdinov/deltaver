# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Npmjs package list."""

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
            with suppress(InvalidVersionError, IndexError, KeyError):
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
