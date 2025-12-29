# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Cached packages list."""

from collections.abc import Sequence
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.package import Package
from deltaver._internal.version_list import VersionList


@final
@attrs.define
class CachedPackageList(VersionList):  # noqa: PEO200. Class for caching
    """Cached packages list."""

    _origin: VersionList
    _cache_value: Sequence[Package]
    _cached: bool

    @classmethod
    def ctor(cls, origin: VersionList) -> VersionList:
        """Ctor."""
        return cls(origin, [], cached=False)

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        if self._cached:
            return self._cache_value
        self._cache_value = self._origin.as_list()
        return self._cache_value
