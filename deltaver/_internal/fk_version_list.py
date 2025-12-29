# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fake version list."""

from collections.abc import Sequence
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.package import Package
from deltaver._internal.version_list import VersionList


@final
@attrs.define(frozen=True)
class FkVersionList(VersionList):
    """Fake version list."""

    _packages: Sequence[Package]

    @override
    def as_list(self) -> Sequence[Package]:
        """List representation."""
        return self._packages
