# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Filtered packages list."""

import string
from collections.abc import Sequence
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.package import Package
from deltaver._internal.version_list import VersionList


@final
@attrs.define(frozen=True)
class FilteredPackageList(VersionList):
    """Filtered packages list."""

    _origin: VersionList

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        packages = []
        for package in self._origin.as_list():
            if set(string.ascii_letters).intersection(str(package.version())):
                continue
            packages.append(package)
        return packages
