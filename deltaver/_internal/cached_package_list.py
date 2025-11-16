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

"""Cached packages list."""

from collections.abc import Sequence
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.package import Package
from deltaver._internal.version_list import VersionList


@final
@attrs.define
# Class for caching
class CachedPackageList(VersionList):  # noqa: PEO200
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
