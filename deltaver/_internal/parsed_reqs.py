# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Parsed requirements protocol."""

from typing import Protocol


class ParsedReqs(Protocol):
    """Parsed requirements protocol."""

    def reqs(self) -> list[tuple[str, str]]:
        """Parsed requirements list."""
