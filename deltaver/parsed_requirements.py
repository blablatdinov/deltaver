import re
from pathlib import Path
from typing import Protocol, final

import attrs
import toml
import typer
from rich import print

from deltaver.config import Config


class ParsedReqs(Protocol):

    def reqs(self) -> list[tuple[str, str]]: ...


@final
@attrs.define(frozen=True)
class FreezedReqs(ParsedReqs):

    _path: Path

    def reqs(self) -> list[tuple[str, str]]:
        res = []
        lines = self._path.read_text().strip().splitlines()
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
    _config: Config

    def reqs(self) -> list[tuple[str, str]]:
        excluded_packages_set = {package.lower() for package in self._config.value_of('excluded')}
        return [
            item
            for item in self._origin.reqs()
            if item[0].lower() not in excluded_packages_set
        ]


@final
@attrs.define(frozen=True)
class PoetryLockReqs(ParsedReqs):

    _path: Path

    def reqs(self) -> list[tuple[str, str]]:
        data = toml.loads(self._path.read_text())
        return [
            (dependency['name'], dependency['version'])
            for dependency in data['package']
        ]


@final
@attrs.define(frozen=True)
class FileNotFoundSafeReqs(ParsedReqs):

    _origin: ParsedReqs

    def reqs(self) -> list[tuple[str, str]]:
        try:
            return self._origin.reqs()
        except FileNotFoundError:
            print('Requirements file not found')
            typer.Exit(1)
