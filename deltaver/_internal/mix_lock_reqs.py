# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Parsed mix.lock requirements file."""

import re
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.parsed_reqs import ParsedReqs


@final
@attrs.define(frozen=True)
class MixLockReqs(ParsedReqs):
    """Parsed mix.lock requirements file."""

    _requirements_file_content: str

    @override
    def reqs(self) -> list[tuple[str, str]]:
        """Parsed mix.lock requirements file."""
        dependencies = []
        pattern = r'"([^"]+)":\s*\{:hex,\s*:[^,]+,\s*"([^"]+)"'
        matches = re.findall(pattern, self._requirements_file_content)
        for package_name, version in matches:
            dependencies.append((package_name, version))
        return dependencies
