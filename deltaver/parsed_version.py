"""Module for parsing version strings into semantic version objects."""

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

from typing import final

import attrs
from semver import VersionInfo

from deltaver.exceptions import InvalidVersionError

# Constants for version parsing
MIN_VERSION_PARTS = 2
MIN_INDEX_FOR_PRE_RELEASE = 1


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
        origin = self._handle_dev_versions(origin)
        origin = self._handle_all_pre_release_versions(origin)
        try:
            return VersionInfo.parse(origin)
        except ValueError as err:
            raise InvalidVersionError(self._version) from err

    def _handle_dev_versions(self, origin: str) -> str:
        """Handle dev versions: 0.13.dev0 -> 0.13.0-dev0, 0.13.0.dev1 -> 0.13.0-dev1."""
        if '.dev' not in origin:
            return origin
        parts = origin.split('.dev')
        if len(parts) != MIN_VERSION_PARTS:
            return origin
        version_part = parts[0]
        dev_number = parts[1]
        version_parts = version_part.split('.')
        if len(version_parts) == MIN_VERSION_PARTS:
            return f'{version_part}.0-dev{dev_number}'
        return f'{version_part}-dev{dev_number}'

    def _handle_all_pre_release_versions(self, origin: str) -> str:
        """Handle all PyPI pre-release versions: beta, alpha, and rc."""
        # Handle beta versions: 0.15.0b1 -> 0.15.0-b1
        origin = self._process_single_char_pre_release(origin, 'b', ['-b', '-beta'])
        # Handle alpha versions: 0.15.0a1 -> 0.15.0-a1
        origin = self._process_single_char_pre_release(origin, 'a', ['-a', '-alpha'])
        # Handle rc versions: 0.15.0rc1 -> 0.15.0-rc1
        origin = self._process_rc_version(origin)
        return origin

    def _process_single_char_pre_release(
        self, origin: str, character: str, suffixes: list[str]
    ) -> str:
        """Process single character pre-release version."""
        # Check if processing should be skipped
        if character not in origin or origin.endswith(character):
            return origin
        if any(suffix in origin for suffix in suffixes):
            return origin
        # Process the version
        for index, current_char in enumerate(origin):
            if self._is_valid_pre_release_position(origin, index, current_char, character):
                prefix = origin[:index]
                suffix = origin[index + 1:]
                return f'{prefix}-{character}{suffix}'
        return origin

    def _is_valid_pre_release_position(
        self, origin: str, index: int, current_char: str, character: str
    ) -> bool:
        """Check if the current position is valid for pre-release processing."""
        if current_char != character or index <= 0:
            return False
        if index + 1 >= len(origin):
            return False
        prev_char_is_digit = origin[index - 1].isdigit()
        next_char_is_digit = origin[index + 1].isdigit()
        return prev_char_is_digit and next_char_is_digit

    def _process_rc_version(self, origin: str) -> str:
        """Process rc version by replacing 'rc' with '-rc'."""
        rc_suffixes = ['-rc']
        if 'rc' not in origin or any(suffix in origin for suffix in rc_suffixes):
            return origin
        return origin.replace('rc', '-rc')
