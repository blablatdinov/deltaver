import datetime

import pytest

from deltaver.delta import DaysDelta
from deltaver.package import FkPackage, FkVersionList


@pytest.fixture()
def packages():
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


def test(packages):
    """Test DaysDelta class.

    https://www.timeanddate.com/date/durationresult.html?d1=20&m1=12&y1=2023&d2=28&m2=6&y2=2024
    """
    assert DaysDelta('0.25.2', packages, datetime.date(2024, 6, 28)).days() == 191
