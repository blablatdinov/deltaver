# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Parsed golang go.sum requirements file."""

from itertools import groupby
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.exceptions import InvalidVersionError
from deltaver._internal.parsed_reqs import ParsedReqs
from deltaver._internal.parsed_version import ParsedVersion


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
