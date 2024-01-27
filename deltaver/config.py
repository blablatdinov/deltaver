from pathlib import Path
from typing import Protocol, TypedDict, final

import attrs
import toml


@final
class PyprojectNotContainDeltaverConfigError(Exception): pass


class ConfigDict(TypedDict):

    fail_on_avg: int
    fail_on_max: int
    excluded: list[str]


class Config(Protocol):

    def value_of(self, value: str): ...


@final
@attrs.define(frozen=True)
class PyprojectTomlConfig(Config):

    _path: Path

    def value_of(self, value: str):
        try:
            deltaver_config = toml.loads(self._path.read_text())['tool']['deltaver']
        except KeyError:
            raise PyprojectNotContainDeltaverConfigError
        return deltaver_config[value]
        


@final
@attrs.define(frozen=True)
class CliOrPyprojectConfig(Config):

    _pyproject_config: Config
    _cli_configs: ConfigDict

    def value_of(self, value: str):
        try:
            return self._pyproject_config.value_of(value)
        except (KeyError, PyprojectNotContainDeltaverConfigError):
            return self._cli_configs[value]
