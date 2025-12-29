# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Sorted package list."""

from collections.abc import Sequence
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.package import Package
from deltaver._internal.version_list import VersionList


@final
@attrs.define(frozen=True)
class SortedPackageList(VersionList):
    """Sorted package list."""

    _origin: VersionList

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        return sorted(
            self._origin.as_list(),
            key=lambda pkg: pkg.version(),
        )
