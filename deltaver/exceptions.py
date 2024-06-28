from typing import final


@final
class NextVersionNotFoundError(Exception):
    pass


@final
class VersionNotFoundError(Exception):
    pass
