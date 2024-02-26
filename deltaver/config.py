import datetime
import enum
from pathlib import Path
from typing import TypedDict


@enum.unique
class Langs(enum.Enum):

    python = 'py'
    javascript = 'js'


@enum.unique
class Formats(enum.Enum):

    freezed = 'freezed'
    lock = 'lock'


class ConfigDict(TypedDict):

    path_to_requirements_file: Path
    file_format: Formats
    fail_on_avg: int
    fail_on_max: int
    artifactory_domain: str
    excluded: list[str]
    for_date: datetime.date
    lang: Langs
