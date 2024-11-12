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

"""Unit test of package."""

import datetime
from pathlib import Path

import pytest
import httpx

from deltaver.package import (
    FilteredPackageList,
    FkPackage,
    FkVersionList,
    PypiPackage,
    PypiPackageList,
    SortedPackageList,
)


@pytest.fixture
def _pypi_mock(respx_mock):
    respx_mock.get('https://pypi.org/pypi/smmap/json').mock(return_value=httpx.Response(
        status_code=200,
        text=Path('tests/fixtures/smmap_pypi_response.json').read_text(),
    ))


def test() -> None:
    """Test pypi package."""
    package = PypiPackage(
        'httpx',
        '0.25.2',
        FkVersionList([
            FkPackage('httpx', '0.25.2', datetime.date(2023, 11, 24)),
            FkPackage('httpx', '0.26.0', datetime.date(2023, 12, 20)),
            FkPackage('httpx', '0.27.0', datetime.date(2024, 2, 21)),
        ]),
    )

    assert package.release_date() == datetime.date(2023, 11, 24)


@pytest.mark.skip
def test_package_list() -> None:
    """Test package list.

    TODO: implement mock and write assert
    """
    PypiPackageList('httpx').as_list()


def test_filtered_package_list() -> None:
    """Test filtered package list."""
    package_list = FilteredPackageList(
        FkVersionList([
            FkPackage('httpx', '0.26.0', datetime.date(2023, 12, 20)),
            FkPackage('httpx', '0.27.0-dev', datetime.date(2023, 12, 20)),
            FkPackage('httpx', '0.27.0', datetime.date(2023, 12, 20)),
        ]),
    ).as_list()

    assert [
        str(package.version())
        for package in package_list
    ] == [
        '0.26.0',
        '0.27.0',
    ]


def test_sorted_package_list() -> None:
    """Test sorted package list."""
    package_list = SortedPackageList(
        FkVersionList([
            FkPackage('httpx', '3.26.0', datetime.date(2023, 12, 20)),
            FkPackage('httpx', '1.27.0', datetime.date(2023, 12, 20)),
            FkPackage('httpx', '2.27.0', datetime.date(2023, 12, 20)),
        ]),
    ).as_list()

    assert [
        str(package.version())
        for package in package_list
    ] == [
        '1.27.0',
        '2.27.0',
        '3.26.0',
    ]


@pytest.mark.usefixtures('_pypi_mock')
def test_skip_removed():
    got = PypiPackageList('smmap').as_list()

    assert '6.0.0' not in [elem.version() for elem in got]
