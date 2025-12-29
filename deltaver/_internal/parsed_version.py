# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Module for parsing version strings into semantic version objects."""

from typing import final

import attrs
from packaging import version as packaging_version

from deltaver._internal.exceptions import InvalidVersionError


@final
@attrs.define(frozen=True)
class ParsedVersion:
    """Parsed version."""

    _version: str

    def origin(self) -> str:
        """Original version."""
        return self._version

    def valid(self) -> bool:
        """Version valid."""
        try:
            self.parse()
        except InvalidVersionError:
            return False
        else:
            return True

    def parse(self) -> packaging_version.Version:
        """Parse version."""
        origin = self._version.removeprefix('v')
        try:
            return packaging_version.parse(origin)
        except packaging_version.InvalidVersion as err:
            raise InvalidVersionError(self._version) from err
