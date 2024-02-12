import datetime
from typing import Protocol


class Package(Protocol):

    def next(self) -> 'Package': ...
    def release_date(self) -> datetime.date: ...
