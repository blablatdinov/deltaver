# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Config dict."""

# noqa: FOC100. Data structures

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, final

from deltaver._internal.formats import Formats


@final
class CliInputConfig(TypedDict):
    """Structure description for CLI input."""

    path_to_file: Path
    file_format: Formats
    excluded: list[str]
    fail_on_avg: int | None
    fail_on_max: int | None


@final
class PyprojectConfig(TypedDict):
    """Structure description for pyproject input."""

    path_to_file: Path | None
    file_format: Formats | None
    excluded: list[str]
    fail_on_avg: int | None
    fail_on_max: int | None


@final
class Config(TypedDict):
    """Config dict."""

    path_to_file: Path
    file_format: Formats
    excluded: list[str]
    fail_on_avg: int
    fail_on_max: int
