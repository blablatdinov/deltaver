# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Version delta protocol."""

import datetime
from typing import Protocol

from typing_extensions import TypeAlias

VersionNumber: TypeAlias = str
UploadTime: TypeAlias = datetime.date
SortedVersionsList: TypeAlias = list[dict[VersionNumber, UploadTime]]


class VersionDelta(Protocol):
    """Version delta protocol."""

    def days(self) -> int:
        """Delta in days."""
