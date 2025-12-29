# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Filter decorator for requirements."""

from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.parsed_reqs import ParsedReqs


@final
@attrs.define(frozen=True)
class ExcludedReqs(ParsedReqs):
    """Filter decorator for requirements."""

    _origin: ParsedReqs
    _excluded_reqs: list[str]

    @override
    def reqs(self) -> list[tuple[str, str]]:
        """Filtered requirements."""
        excluded_packages_set = {package.lower() for package in self._excluded_reqs}
        return [
            package
            for package in self._origin.reqs()
            if package[0].lower() not in excluded_packages_set
        ]
