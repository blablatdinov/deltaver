# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Overtaking safe version delta."""

from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.exceptions import TargetGreaterLastError
from deltaver._internal.version_delta import VersionDelta


@final
@attrs.define(frozen=True)
class OvertakingSafeVersionDelta(VersionDelta):
    """Overtaking safe version delta."""

    _origin: VersionDelta
    _enable: bool

    @override
    def days(self) -> int:
        """Delta in days."""
        try:
            return self._origin.days()
        except TargetGreaterLastError:
            return 0
