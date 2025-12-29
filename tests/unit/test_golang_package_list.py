# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test golang package list."""

import datetime
import json

import pytest
from httpx import Response
from respx.router import MockRouter

from deltaver._internal.fk_package import FkPackage
from deltaver._internal.golang_package_list import GolangPackageList


@pytest.fixture
def _mock_golang_proxy(respx_mock: MockRouter) -> None:
    versions = [
        'v2.0.0',
        'v2.0.1',
        'v2.0.2',
        'v2.0.3',
        'v2.0.4',
        'v2.0.5',
        'v2.0.6',
    ]
    dates = [
        '2019-03-14T23:30:15Z',
        '2021-07-16T23:20:56Z',
        '2022-04-22T22:25:44Z',
        '2023-10-10T18:05:46Z',
        '2024-03-18T16:06:27Z',
        '2024-09-16T17:36:36Z',
        '2024-12-16T17:50:50Z',
    ]
    respx_mock.get('https://proxy.golang.org/github.com/cpuguy83/go-md2man/v2/@v/list').mock(return_value=Response(
        200, text='\n'.join(versions),
    ))
    for ver, date in zip(versions, dates):
        (
            respx_mock
            .get('https://proxy.golang.org/github.com/cpuguy83/go-md2man/v2/@v/{0}.info'.format(ver))
            .mock(return_value=Response(
                200,
                text=json.dumps({
                    'Version': ver,
                    'Time': date,
                }),
            ))
        )


@pytest.mark.usefixtures('_mock_golang_proxy')
def test() -> None:
    """Test golang package list."""
    package = 'github.com/cpuguy83/go-md2man/v2'
    got = GolangPackageList(package).as_list()

    assert got == [
        FkPackage(package, 'v2.0.0', datetime.date(2019, 3, 14)),
        FkPackage(package, 'v2.0.1', datetime.date(2021, 7, 16)),
        FkPackage(package, 'v2.0.2', datetime.date(2022, 4, 22)),
        FkPackage(package, 'v2.0.3', datetime.date(2023, 10, 10)),
        FkPackage(package, 'v2.0.4', datetime.date(2024, 3, 18)),
        FkPackage(package, 'v2.0.5', datetime.date(2024, 9, 16)),
        FkPackage(package, 'v2.0.6', datetime.date(2024, 12, 16)),
    ]
