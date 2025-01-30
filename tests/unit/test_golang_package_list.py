# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import datetime
import json

import pytest
from httpx import Response
from respx.router import MockRouter

from deltaver.fk_package import FkPackage
from deltaver.golang_package_list import GolangPackageList


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
        datetime.datetime(2019, 3, 14, 23, 30, 15),
        datetime.datetime(2021, 7, 16, 23, 20, 56),
        datetime.datetime(2022, 4, 22, 22, 25, 44),
        datetime.datetime(2023, 10, 10, 18, 5, 46),
        datetime.datetime(2024, 3, 18, 16, 6, 27),
        datetime.datetime(2024, 9, 16, 17, 36, 36),
        datetime.datetime(2024, 12, 16, 17, 50, 50),
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
                    'Time': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                }),
            ))
        )


@pytest.mark.usefixtures('_mock_golang_proxy')
def test():
    got = GolangPackageList(
        'github.com/cpuguy83/go-md2man/v2',
    ).as_list()

    assert got == [
        FkPackage('github.com/cpuguy83/go-md2man/v2', 'v2.0.0', datetime.datetime(2019, 3, 14, 23, 30, 15)),
        FkPackage('github.com/cpuguy83/go-md2man/v2', 'v2.0.1', datetime.datetime(2021, 7, 16, 23, 20, 56)),
        FkPackage('github.com/cpuguy83/go-md2man/v2', 'v2.0.2', datetime.datetime(2022, 4, 22, 22, 25, 44)),
        FkPackage('github.com/cpuguy83/go-md2man/v2', 'v2.0.3', datetime.datetime(2023, 10, 10, 18, 5, 46)),
        FkPackage('github.com/cpuguy83/go-md2man/v2', 'v2.0.4', datetime.datetime(2024, 3, 18, 16, 6, 27)),
        FkPackage('github.com/cpuguy83/go-md2man/v2', 'v2.0.5', datetime.datetime(2024, 9, 16, 17, 36, 36)),
        FkPackage('github.com/cpuguy83/go-md2man/v2', 'v2.0.6', datetime.datetime(2024, 12, 16, 17, 50, 50)),
    ]
