# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Decrement delta."""

import datetime
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.version_delta import VersionDelta


@final
@attrs.define(frozen=True)
class DecrDelta(VersionDelta):
    """Decrement delta."""

    _origin: VersionDelta
    _for_date: datetime.date

    @override
    def days(self) -> int:
        """Delta in days."""
        today = datetime.datetime.now(tz=datetime.timezone.utc).date()
        recalculated_days = self._origin.days() - (today - self._for_date).days
        return max(recalculated_days, 0)
