# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Exceptions."""

from typing import final


@final
class NextVersionNotFoundError(Exception):
    """Next version not found error."""


@final
class VersionNotFoundError(Exception):
    """Version not found error."""


@final
class TargetGreaterLastError(Exception):
    """Target greater last error."""


@final
class InvalidVersionError(Exception):
    """Invalid version."""


@final
class ThresholdReachedError(Exception):
    """Threshold Reached Error."""
