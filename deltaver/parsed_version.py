# The MIT License (MIT).
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
        """Convert dev version to semver format."""
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
        """Convert beta version to semver format."""
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
class AlphaCorrectVersion(SupportsStr):
    """Alpha correct version."""

    _origin: SupportsStr

    def __str__(self) -> str:
        """Convert alpha version to semver format."""
        origin = str(self._origin)
        if '-a' in origin or 'a' not in origin:
            return origin
        return self._process_alpha_version(origin)

    def _process_alpha_version(self, origin: str) -> str:
        """Process alpha version by finding and replacing 'a' with '-a'."""
        for index, current_char in enumerate(origin):
            if self._is_valid_alpha_position(origin, index, current_char):
                prefix = origin[:index]
                suffix = origin[index + 1:]
                return f'{prefix}-a{suffix}'
        return origin

    def _is_valid_alpha_position(self, origin: str, index: int, current_char: str) -> bool:
        """Check if position is valid for alpha processing."""
        if current_char != 'a' or index <= 0:
            return False
        if index + 1 >= len(origin):
            return origin[index - 1].isdigit()
        prev_char_is_digit = origin[index - 1].isdigit()
        next_char_is_digit = origin[index + 1].isdigit()
        return prev_char_is_digit and next_char_is_digit


@final
@attrs.define(frozen=True)
class PostCorrectVersion(SupportsStr):
    """Post correct version."""

    _origin: SupportsStr

    def __str__(self) -> str:
        """Convert post-release version to semver format."""
        origin = str(self._origin)
        if '.post' in origin:
            origin = origin.replace('.post', '+post')
        return origin


@final
@attrs.define(frozen=True)
class ZeroBeforeIntCorrectVersion(SupportsStr):
    """Zero before int correct version."""

    _origin: SupportsStr

    def __str__(self) -> str:
        """Normalize version by removing leading zeros."""
        origin = str(self._origin)
        # Split by dots and remove leading zeros from each part
        parts = origin.split('.')
        normalized_parts = [self._normalize_part(part) for part in parts]
        return '.'.join(normalized_parts)

    def _normalize_part(self, part: str) -> str:
        """Normalize a version part by removing leading zeros."""
        try:
            return str(int(part))
        except ValueError:
            return part


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
                    ZeroBeforeIntCorrectVersion(
                        PostCorrectVersion(
                            AlphaCorrectVersion(
                                BetaCorrectVersion(
                                    DevCorrectVersion(
                                        FkSupportsStr(origin),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        except ValueError as err:
            raise InvalidVersionError(self._version) from err
