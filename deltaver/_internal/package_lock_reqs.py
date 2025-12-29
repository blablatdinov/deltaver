# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Parsed package-lock.json requirements file."""

import json
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.parsed_reqs import ParsedReqs


@final
@attrs.define(frozen=True)
class PackageLockReqs(ParsedReqs):
    """Parsed package-lock.json requirements file."""

    _lock_file_content: str

    @override
    def reqs(self) -> list[tuple[str, str]]:
        """Parsed package-lock.json requirements file."""
        parsed_json = json.loads(self._lock_file_content)
        return [
            (name, version_info['version'])
            for name, version_info in parsed_json['dependencies'].items()
        ]
