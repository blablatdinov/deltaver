# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Config dict."""

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
