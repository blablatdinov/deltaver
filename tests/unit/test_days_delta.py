# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Unit test of delta."""

import datetime

import pytest

from deltaver._internal.days_delta import DaysDelta
from deltaver._internal.fk_package import FkPackage
from deltaver._internal.fk_version_list import FkVersionList
from deltaver._internal.version_list import VersionList


@pytest.fixture
def packages() -> VersionList:
    """Fake packages."""
    return FkVersionList([
        FkPackage(
            'httpx',
            '0.25.2',
            datetime.date(2023, 11, 24),
        ),
        FkPackage(
            'httpx',
            '0.26.0',
            datetime.date(2023, 12, 20),
        ),
    ])


def test(packages: VersionList) -> None:
    """Test DaysDelta class.

    https://www.timeanddate.com/date/durationresult.html?d1=20&m1=12&y1=2023&d2=28&m2=6&y2=2024
    """
    assert DaysDelta(
        '0.25.2',
        packages,
        datetime.date(2024, 6, 28),
    ).days() == 191
