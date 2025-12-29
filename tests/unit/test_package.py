# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Unit test of package."""

import datetime
from pathlib import Path

import httpx
import pytest
import respx

from deltaver._internal.filtered_package_list import FilteredPackageList
from deltaver._internal.fk_package import FkPackage
from deltaver._internal.fk_version_list import FkVersionList
from deltaver._internal.pypi_package import PypiPackage
from deltaver._internal.pypi_package_list import PypiPackageList
from deltaver._internal.sorted_package_list import SortedPackageList


@pytest.fixture
def _pypi_mock(respx_mock: respx.router.MockRouter) -> None:
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
def test_skip_removed() -> None:
    """Test skip yanked versions."""
    got = PypiPackageList('smmap').as_list()

    assert len(got) == 15
    assert '6.0.0' not in {elem.version() for elem in got}
