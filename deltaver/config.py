import enum
from pathlib import Path
from typing import Protocol, TypedDict, TypeVar, final

import attrs
import toml

ConfigValueT = TypeVar('ConfigValueT')


@final
class PyprojectNotContainDeltaverConfigError(Exception):
    pass


class Formats(enum.Enum):

    freezed = 'freezed'
    lock = 'lock'


class ConfigDict(TypedDict):

    file_format: Formats
    fail_on_avg: int
    fail_on_max: int
    artifactory_domain: str
    excluded: list[str]


class Config(Protocol):

    def value_of(self, value: str) -> ConfigValueT: ...


@final
@attrs.define(frozen=True)
class PyprojectTomlConfig(Config):

    _path: Path

    def value_of(self, value: str) -> ConfigValueT:
        try:
            deltaver_config = toml.loads(self._path.read_text())['tool']['deltaver']
        except KeyError as err:
            raise PyprojectNotContainDeltaverConfigError from err
        return deltaver_config[value]


@final
@attrs.define(frozen=True)
class CliOrPyprojectConfig(Config):

    _pyproject_config: Config
    _cli_configs: ConfigDict

    def value_of(self, value: str) -> ConfigValueT:
        try:
            return self._pyproject_config.value_of(value)
        except (KeyError, PyprojectNotContainDeltaverConfigError):
            return self._cli_configs[value]
