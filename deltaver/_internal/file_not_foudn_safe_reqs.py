# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""File not found safe requirements."""

from typing import final

import attrs
import typer
from rich import print as rich_print
from typing_extensions import override

from deltaver._internal.parsed_reqs import ParsedReqs


@final
@attrs.define(frozen=True)
class FileNotFoundSafeReqs(ParsedReqs):
    """File not found safe requirements."""

    _origin: ParsedReqs

    @override
    def reqs(self) -> list[tuple[str, str]]:
        """File not found safe requirements."""
        try:
            return self._origin.reqs()
        except FileNotFoundError as err:
            rich_print('Requirements file not found')
            raise typer.Exit(1) from err
