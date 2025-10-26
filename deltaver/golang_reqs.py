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

"""Parsed golang go.sum requirements file."""

from itertools import groupby
from typing import final

import attrs
from typing_extensions import override

from deltaver.exceptions import InvalidVersionError
from deltaver.parsed_reqs import ParsedReqs
from deltaver.parsed_version import ParsedVersion


@final
@attrs.define(frozen=True)
class GolangReqs(ParsedReqs):
    """Parsed golang go.sum requirements file."""

    _go_sum_content: str

    @override
    def reqs(self) -> list[tuple[str, str]]:
        """Parsed golang go.sum requirements file."""
        lines = self._go_sum_content.strip().splitlines()
        res = []
        for line in lines:
            if '/go.mod' in line:
                continue
            splitted_line = line.split(' ')
            try:
                ParsedVersion(splitted_line[1]).parse()
            except InvalidVersionError:
                continue
            res.append((
                splitted_line[0],
                splitted_line[1],
            ))
        return self._latest_version(res)

    def _latest_version(
        self,
        packages: list[tuple[str, str]],
    ) -> list[tuple[str, str]]:
        groupped = groupby(
            sorted(
                packages,
                key=lambda pkg_info: (pkg_info[0], ParsedVersion(pkg_info[1]).parse()),
            ),
            key=lambda pkg_info: pkg_info[0],
        )
        actual = []
        for _, pkg_versions in groupped:
            ver = tuple(pkg_versions)[-1]
            actual.append((ver[0], ver[1]))
        return actual
