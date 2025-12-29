# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fake version delta."""

from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.version_delta import VersionDelta


@final
@attrs.define(frozen=True)
class FkVersionDelta(VersionDelta):
    """Fake version delta."""

    _origin: int

    @override
    def days(self) -> int:
        """Delta in days."""
        return self._origin
