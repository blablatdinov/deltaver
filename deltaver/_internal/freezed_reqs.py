# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Requirements from `pip freeze` format."""

import re
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.parsed_reqs import ParsedReqs


@final
@attrs.define(frozen=True)
class FreezedReqs(ParsedReqs):
    """Requirements from `pip freeze` format."""

    _requirements_file_content: str

    @override
    def reqs(self) -> list[tuple[str, str]]:  # noqa: WPS210. Simplify later
        """Parsed requirements list."""
        res = []
        lines = self._requirements_file_content.splitlines()
        expected_splitted_line_len = 2
        for line in lines:
            splitted_line = line.split(';')[0].split('==')
            if len(splitted_line) != expected_splitted_line_len:
                continue
            package, version = splitted_line
            package = re.sub(r'\[.*?\]', '', package)
            res.append((package, version.strip()))
        return res
