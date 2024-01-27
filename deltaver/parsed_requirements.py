
import re
from pathlib import Path
from typing import Protocol, final

import attrs
import toml


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
class PoetryLockReqs(ParsedReqs):

    _path: Path

    def reqs(self) -> list[tuple[str, str]]:
        data = toml.loads(self._path.read_text())
        return [
            (dependency['name'], dependency['version'])
            for dependency in data['package']
        ]
