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

import json
import re
from typing import Protocol, final

import attrs
import toml
import typer
from rich import print


class ParsedReqs(Protocol):

    def reqs(self) -> list[tuple[str, str]]: ...


@final
@attrs.define(frozen=True)
class FreezedReqs(ParsedReqs):

    _requirements_file_content: str

    def reqs(self) -> list[tuple[str, str]]:
        res = []
        lines = self._requirements_file_content.splitlines()
        expected_splitted_line_len = 2
        for line in lines:
            splitted_line = line.split(';')[0].split('==')
            if len(splitted_line) != expected_splitted_line_len:
                continue
            package, version = splitted_line
            package = re.sub(r'\[.*?\]', '', package)
            res.append((package, version.strip()))
        return res


@final
@attrs.define(frozen=True)
class ExcludedReqs(ParsedReqs):

    _origin: ParsedReqs
    _excluded_reqs: list[str]

    def reqs(self) -> list[tuple[str, str]]:
        excluded_packages_set = {package.lower() for package in self._excluded_reqs}
        return [
            item
            for item in self._origin.reqs()
            if item[0].lower() not in excluded_packages_set
        ]


@final
@attrs.define(frozen=True)
class PoetryLockReqs(ParsedReqs):

    _requirements_file_content: str

    def reqs(self) -> list[tuple[str, str]]:
        parsed_toml = toml.loads(self._requirements_file_content)
        return [
            (dependency['name'], dependency['version'])
            for dependency in parsed_toml['package']
        ]


@final
@attrs.define(frozen=True)
class FileNotFoundSafeReqs(ParsedReqs):

    _origin: ParsedReqs

    def reqs(self) -> list[tuple[str, str]]:
        try:
            return self._origin.reqs()
        except FileNotFoundError as err:
            print('Requirements file not found')
            raise typer.Exit(1) from err


@final
@attrs.define(frozen=True)
class PackageLockReqs(ParsedReqs):

    _lock_file_content: str

    def reqs(self) -> list[tuple[str, str]]:
        parsed_json = json.loads(self._lock_file_content)
        return [
            (name, version_info['version'])
            for name, version_info in parsed_json['dependencies'].items()
        ]
