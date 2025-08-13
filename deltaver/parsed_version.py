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
        origin = self._version
        if origin.startswith('v'):
            origin = origin[1:]
        
        # Handle dev versions: 0.13.dev0 -> 0.13.0-dev0, 0.13.0.dev1 -> 0.13.0-dev1
        if '.dev' in origin:
            parts = origin.split('.dev')
            if len(parts) == 2:
                version_part = parts[0]
                dev_number = parts[1]
                version_parts = version_part.split('.')
                if len(version_parts) == 2:
                    origin = f"{version_part}.0-dev{dev_number}"
                else:
                    origin = f"{version_part}-dev{dev_number}"
        
        # Handle PyPI beta versions: 0.15.0b1 -> 0.15.0-b1
        if 'b' in origin and not origin.endswith('b') and not any(x in origin for x in ['-b', '-beta']):
            # Find the position of 'b' that's not part of a larger word
            for i, char in enumerate(origin):
                if char == 'b' and i > 0 and origin[i-1].isdigit() and i+1 < len(origin) and origin[i+1].isdigit():
                    origin = origin[:i] + '-b' + origin[i+1:]
                    break
        
        # Handle PyPI alpha versions: 0.15.0a1 -> 0.15.0-a1
        if 'a' in origin and not origin.endswith('a') and not any(x in origin for x in ['-a', '-alpha']):
            for i, char in enumerate(origin):
                if char == 'a' and i > 0 and origin[i-1].isdigit() and i+1 < len(origin) and origin[i+1].isdigit():
                    origin = origin[:i] + '-a' + origin[i+1:]
                    break
        
        # Handle PyPI rc versions: 0.15.0rc1 -> 0.15.0-rc1
        if 'rc' in origin and not any(x in origin for x in ['-rc']):
            origin = origin.replace('rc', '-rc')
        
        try:
            return VersionInfo.parse(origin)
        except ValueError:
            raise InvalidVersionError(self._version)
