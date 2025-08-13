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
class DevVersionProcessor:
    """Processor for dev versions."""

    def process(self, origin: str) -> str:
        """Handle dev versions: 0.13.dev0 -> 0.13.0-dev0, 0.13.0.dev1 -> 0.13.0-dev1."""
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
class PreReleaseProcessor:
    """Processor for pre-release versions."""

    def process_beta(self, origin: str) -> str:
        """Process beta versions: 0.15.0b1 -> 0.15.0-b1."""
        return self._process_single_char(origin, 'b', ['-b', '-beta'])

    def process_alpha(self, origin: str) -> str:
        """Process alpha versions: 0.15.0a1 -> 0.15.0-a1."""
        return self._process_single_char(origin, 'a', ['-a', '-alpha'])

    def _process_single_char(self, origin: str, character: str, suffixes: list[str]) -> str:
        """Process single character pre-release version."""
        if character not in origin or origin.endswith(character):
            return origin
        if any(suffix in origin for suffix in suffixes):
            return origin
        return self._find_and_replace_character(origin, character)

    def _find_and_replace_character(self, origin: str, character: str) -> str:
        """Find and replace character with '-character'."""
        origin_length = len(origin)
        for index in range(origin_length):
            is_valid = self._is_valid_position(origin, index, origin[index], character)
            if is_valid:
                prefix = origin[:index]
                suffix = origin[index + 1:]
                return f'{prefix}-{character}{suffix}'
        return origin

    def _is_valid_position(self, origin: str, index: int, current_char: str, character: str) -> bool:
        """Check if position is valid for pre-release processing."""
        if current_char != character or index <= 0:
            return False
        if index + 1 >= len(origin):
            return False
        prev_char_is_digit = origin[index - 1].isdigit()
        next_char_is_digit = origin[index + 1].isdigit()
        return prev_char_is_digit and next_char_is_digit


@final
@attrs.define(frozen=True)
class RcAndPostProcessor:
    """Processor for rc and post-release versions."""

    def process(self, origin: str) -> str:
        """Process rc and post-release versions."""
        # Handle rc versions: 0.15.0rc1 -> 0.15.0-rc1
        rc_suffixes = ['-rc']
        if 'rc' in origin and not any(suffix in origin for suffix in rc_suffixes):
            origin = origin.replace('rc', '-rc')
        # Handle post-release versions: 4.6.2.post1 -> 4.6.2+post1
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
        # Process with different processors
        dev_processor = DevVersionProcessor()
        pre_release_processor = PreReleaseProcessor()
        rc_post_processor = RcAndPostProcessor()
        origin = dev_processor.process(origin)
        origin = pre_release_processor.process_beta(origin)
        origin = pre_release_processor.process_alpha(origin)
        origin = rc_post_processor.process(origin)
        try:
            return VersionInfo.parse(origin)
        except ValueError as err:
            raise InvalidVersionError(self._version) from err
