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

    def _handle_beta_versions(self, origin: str) -> str:
        """Handle PyPI beta versions: 0.15.0b1 -> 0.15.0-b1."""
        if 'b' not in origin or origin.endswith('b') or any(x in origin for x in ['-b', '-beta']):
            return origin

        for i, char in enumerate(origin):
            if (char == 'b' and i > 0 and origin[i-1].isdigit() and
                i+1 < len(origin) and origin[i+1].isdigit()):
                return origin[:i] + '-b' + origin[i+1:]
        return origin

    def _handle_alpha_versions(self, origin: str) -> str:
        """Handle PyPI alpha versions: 0.15.0a1 -> 0.15.0-a1."""
        if 'a' not in origin or origin.endswith('a') or any(x in origin for x in ['-a', '-alpha']):
            return origin

        for i, char in enumerate(origin):
            if (char == 'a' and i > 0 and origin[i-1].isdigit() and
                i+1 < len(origin) and origin[i+1].isdigit()):
                return origin[:i] + '-a' + origin[i+1:]
        return origin

    def _handle_rc_versions(self, origin: str) -> str:
        """Handle PyPI rc versions: 0.15.0rc1 -> 0.15.0-rc1."""
        if 'rc' not in origin or any(x in origin for x in ['-rc']):
            return origin
        return origin.replace('rc', '-rc')

    def parse(self) -> VersionInfo:
        """Parse version."""
        origin = self._version.removeprefix('v')
        origin = self._handle_dev_versions(origin)
        origin = self._handle_beta_versions(origin)
        origin = self._handle_alpha_versions(origin)
        origin = self._handle_rc_versions(origin)

        try:
            return VersionInfo.parse(origin)
        except ValueError as err:
            raise InvalidVersionError(self._version) from err
