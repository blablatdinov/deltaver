# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Package."""

import datetime
from typing import Protocol

from packaging.version import Version


class Package(Protocol):
    """Package."""

    def version(self) -> Version:
        """Version."""

    def name(self) -> str:
        """Name."""

    def release_date(self) -> datetime.date:
        """Release date."""
