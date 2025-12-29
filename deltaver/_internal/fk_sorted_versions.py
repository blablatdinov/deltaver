# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fake sorted versions."""

from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.sorted_versions import SortedVersions
from deltaver._internal.version_delta import SortedVersionsList


@final
@attrs.define(frozen=True)
class FkSortedVersions(SortedVersions):
    """Fake sorted versions."""

    _origin: SortedVersionsList

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        return self._origin
