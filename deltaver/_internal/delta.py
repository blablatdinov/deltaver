# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Delta."""

from typing import Protocol

import attrs


@attrs.define(frozen=True)
class Delta(Protocol):
    """Delta."""

    def days(self) -> int:
        """Days of delta."""
