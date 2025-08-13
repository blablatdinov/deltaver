# The MIT License (MIT).  #
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Module for parsing version strings into semantic version objects."""

from typing import final

import attrs
from semver import VersionInfo

from deltaver.exceptions import InvalidVersionError
from deltaver.fk_supports_str import FkSupportsStr
from deltaver.supports_str import SupportsStr

# Constants for version parsing
MIN_VERSION_PARTS = 2
MIN_INDEX_FOR_PRE_RELEASE = 1


@final
@attrs.define(frozen=True)
class DevCorrectVersion(SupportsStr):
    """Dev correct version."""

    _origin: SupportsStr

    def __str__(self) -> str:
        """Return the version as a string."""
        origin = str(self._origin)
        if '.dev' not in origin:
            return origin
        parts = origin.split('.dev')
        if len(parts) != MIN_VERSION_PARTS:
            return origin
        version_part, dev_number = parts[0], parts[1]
        version_parts = version_part.split('.')
        if len(version_parts) == MIN_VERSION_PARTS:
            return f'{version_part}.0-dev{dev_number}'
        return f'{version_part}-dev{dev_number}'


@final
@attrs.define(frozen=True)
class BetaCorrectVersion(SupportsStr):
    """Beta correct version."""

    _origin: SupportsStr

    def __str__(self) -> str:
        """Return the version as a string."""
        origin = str(self._origin)
        if '-b' in origin or 'b' not in origin:
            return origin
        parts = origin.split('b')
        if len(parts) != MIN_VERSION_PARTS:
            return origin
        version_part, beta_number = parts[0], parts[1]
        return f'{version_part}-b{beta_number}'


@final
@attrs.define(frozen=True)
class PostCorrectVersion(SupportsStr):
    """Post correct version."""

    _origin: SupportsStr

    def __str__(self) -> str:
        """Return the version as a string."""
        origin = str(self._origin)
        if '.post' in origin:
            origin = origin.replace('.post', '+post')
        return origin


@final
@attrs.define(frozen=True)
class ParsedVersion:
    """Parsed version."""

    _version: str

    def origin(self) -> str:
        """Original version."""
        return self._version

    def parse(self) -> VersionInfo:
        """Parse version."""
        origin = self._version.removeprefix('v')
        try:
            return VersionInfo.parse(
                str(
                    PostCorrectVersion(
                        BetaCorrectVersion(
                            DevCorrectVersion(
                                FkSupportsStr(origin),
                            ),
                        ),
                    ),
                ),
            )
        except ValueError as err:
            raise InvalidVersionError(self._version) from err
