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
