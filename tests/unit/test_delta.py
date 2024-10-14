# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Unit test of delta."""

import datetime

import pytest

from deltaver.delta import DaysDelta
from deltaver.package import FkPackage, FkVersionList, VersionList


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
    assert DaysDelta('0.25.2', packages, datetime.date(2024, 6, 28)).days() == 191
