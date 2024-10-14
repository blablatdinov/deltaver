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

import pytest

from deltaver.package import (
    FilteredPackageList,
    FkPackage,
    FkVersionList,
    Package,
    PypiPackage,
    PypiPackageList,
    SortedPackageList,
    VersionList,
)


@pytest.fixture
def httpx_27_package() -> Package:
    """Fake package httpx==0.27.0 ."""
    return FkPackage('httpx', '0.27.0', datetime.date(2024, 2, 21))


@pytest.fixture
def package_list(httpx_27_package: Package) -> VersionList:
    """Fake package list."""
    httpx_0_26_0 = FkPackage('httpx', '0.26.0', datetime.date(2023, 12, 20))
    httpx_0_25_2 = FkPackage('httpx', '0.25.2', datetime.date(2023, 11, 24))
    return FkVersionList([httpx_0_25_2, httpx_0_26_0, httpx_27_package])


def test(package_list: VersionList) -> None:
    """Test pypi package."""
    package = PypiPackage(
        'httpx',
        '0.25.2',
        package_list,
    )

    assert package.release_date() == datetime.date(2023, 11, 24)


def test_package_list(httpx_27_package: Package) -> None:
    """Test package list."""
    PypiPackageList('httpx').as_list()

    # FIXME: assert


def test_filtered_package_list(httpx_27_package: Package) -> None:
    """Test filtered package list."""
    package_list = FilteredPackageList(
        PypiPackageList('httpx'),
    ).as_list()

    assert [
        str(package.version())
        for package in package_list
    ] == [
        '0.10.0',
        '0.10.1',
        '0.11.0',
        '0.11.1',
        '0.12.0',
        '0.12.1',
        '0.13.0',
        '0.13.1',
        '0.13.2',
        '0.13.3',
        '0.14.0',
        '0.14.1',
        '0.14.2',
        '0.14.3',
        '0.15.0',
        '0.15.1',
        '0.15.2',
        '0.15.3',
        '0.15.4',
        '0.15.5',
        '0.16.0',
        '0.16.1',
        '0.17.0',
        '0.17.1',
        '0.18.0',
        '0.18.1',
        '0.18.2',
        '0.19.0',
        '0.20.0',
        '0.21.0',
        '0.21.1',
        '0.21.2',
        '0.21.3',
        '0.22.0',
        '0.23.0',
        '0.23.1',
        '0.23.2',
        '0.23.3',
        '0.24.0',
        '0.24.1',
        '0.25.0',
        '0.25.1',
        '0.25.2',
        '0.26.0',
        '0.27.0',
        '0.6.7',
        '0.6.8',
        '0.7.0',
        '0.7.1',
        '0.7.2',
        '0.7.3',
        '0.7.4',
        '0.7.5',
        '0.7.6',
        '0.7.7',
        '0.7.8',
        '0.8.0',
        '0.9.0',
        '0.9.1',
        '0.9.2',
        '0.9.3',
        '0.9.4',
        '0.9.5',
    ]


def test_sorted_package_list(httpx_27_package: Package) -> None:
    """Test sorted package list."""
    package_list = SortedPackageList(
        FilteredPackageList(
            PypiPackageList('httpx'),
        ),
    ).as_list()

    assert [
        str(package.version())
        for package in package_list
    ] == [
        '0.6.7',
        '0.6.8',
        '0.7.0',
        '0.7.1',
        '0.7.2',
        '0.7.3',
        '0.7.4',
        '0.7.5',
        '0.7.6',
        '0.7.7',
        '0.7.8',
        '0.8.0',
        '0.9.0',
        '0.9.1',
        '0.9.2',
        '0.9.3',
        '0.9.4',
        '0.9.5',
        '0.10.0',
        '0.10.1',
        '0.11.0',
        '0.11.1',
        '0.12.0',
        '0.12.1',
        '0.13.0',
        '0.13.1',
        '0.13.2',
        '0.13.3',
        '0.14.0',
        '0.14.1',
        '0.14.2',
        '0.14.3',
        '0.15.0',
        '0.15.1',
        '0.15.2',
        '0.15.3',
        '0.15.4',
        '0.15.5',
        '0.16.0',
        '0.16.1',
        '0.17.0',
        '0.17.1',
        '0.18.0',
        '0.18.1',
        '0.18.2',
        '0.19.0',
        '0.20.0',
        '0.21.0',
        '0.21.1',
        '0.21.2',
        '0.21.3',
        '0.22.0',
        '0.23.0',
        '0.23.1',
        '0.23.2',
        '0.23.3',
        '0.24.0',
        '0.24.1',
        '0.25.0',
        '0.25.1',
        '0.25.2',
        '0.26.0',
        '0.27.0',
    ]
