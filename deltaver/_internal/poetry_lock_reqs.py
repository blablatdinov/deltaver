# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Parsed poetry.lock requirements file."""

from typing import final

import attrs
import toml
from typing_extensions import override

from deltaver._internal.parsed_reqs import ParsedReqs


@final
@attrs.define(frozen=True)
class PoetryLockReqs(ParsedReqs):
    """Parsed poetry.lock requirements file."""

    _requirements_file_content: str

    @override
    def reqs(self) -> list[tuple[str, str]]:
        """Parsed poetry.lock requirements file."""
        parsed_toml = toml.loads(self._requirements_file_content)
        return [
            (dependency['name'], dependency['version'])
            for dependency in parsed_toml['package']
        ]
