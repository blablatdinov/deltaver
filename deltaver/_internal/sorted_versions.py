# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Sorted versions protocol."""

from typing import Protocol

from deltaver._internal.version_delta import SortedVersionsList


class SortedVersions(Protocol):
    """Sorted versions protocol."""

    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
