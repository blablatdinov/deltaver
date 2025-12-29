# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Version list."""

from collections.abc import Sequence
from typing import Protocol

from deltaver._internal.package import Package


class VersionList(Protocol):
    """Version list."""

    def as_list(self) -> Sequence[Package]:
        """List representation."""
