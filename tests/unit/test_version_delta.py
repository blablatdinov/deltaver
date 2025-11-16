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

"""Test version delta."""

import datetime
import os
from collections.abc import Generator
from pathlib import Path
from shutil import copyfile

import httpx
import pytest
from httpx import Response
from respx.router import MockRouter
from time_machine import TimeMachineFixture

from deltaver._internal.cached_sorted_versions import CachedSortedVersions
from deltaver._internal.decr_delta import DecrDelta
from deltaver._internal.fk_version_delta import FkVersionDelta
from deltaver._internal.npmjs_versions_sorted_by_semver import NpmjsVersionsSortedBySemver
from deltaver._internal.pypi_package_list import PypiPackageList


@pytest.fixture
def _mock_pypi(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/httpx/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/httpx_pypi_response.json').read_text(),
    ))


@pytest.fixture
def _mock_eljson(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/eljson/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/eljson_response.json').read_text(),
    ))


@pytest.fixture
def _mock_gitdb(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/gitdb/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/gitdb_response.json').read_text(),
    ))


@pytest.fixture
def _mock_cryptography(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/cryptography/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/cryptography_response.json').read_text(),
    ))


@pytest.fixture
def _mock_greenlet(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/greenlet/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/greenlet_response.json').read_text(),
    ))


@pytest.fixture
def _mock_vue(respx_mock: MockRouter) -> None:
    respx_mock.get('https://registry.npmjs.org/vue').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/vue_npmjs_response.json').read_text(),
    ))


@pytest.fixture
def other_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Change directory to tmp_path."""
    origin_dir = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(origin_dir)


def test_decr_delta(time_machine: TimeMachineFixture) -> None:
    """Test DecrDelta."""
    time_machine.move_to(datetime.datetime(2024, 2, 5, tzinfo=datetime.timezone.utc))
    got = DecrDelta(
        FkVersionDelta(15),
        datetime.datetime(2024, 2, 1, tzinfo=datetime.timezone.utc).date(),
    ).days()

    assert got == 11


def test_negative_decr_delta(time_machine: TimeMachineFixture) -> None:
    """Test negative DecrDelta."""
    time_machine.move_to(datetime.datetime(2024, 2, 5, tzinfo=datetime.timezone.utc))
    got = DecrDelta(
        FkVersionDelta(15),
        datetime.datetime(2020, 2, 1, tzinfo=datetime.timezone.utc).date(),
    ).days()

    assert got == 0


@pytest.fixture
def exist_cache(tmp_path: Path, time_machine: TimeMachineFixture, _mock_pypi: None) -> Generator[Path, None, None]:
    """Create cache files."""
    origin_dir = Path.cwd()
    time_machine.move_to(datetime.datetime(2024, 2, 5, tzinfo=datetime.timezone.utc))
    httpx_cache_dir = tmp_path / '.deltaver_cache/httpx'
    httpx_cache_dir.mkdir(exist_ok=True, parents=True)
    copyfile('tests/fixtures/httpx_pypi_response.json', httpx_cache_dir / '2024-02-05.json')
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(origin_dir)


@pytest.mark.usefixtures('_mock_pypi')
def test_cached_version_delta(other_dir: Path, time_machine: TimeMachineFixture, respx_mock: MockRouter) -> None:
    """Test cached version delta."""
    time_machine.move_to(datetime.datetime(2024, 2, 5, tzinfo=datetime.timezone.utc))
    http_fetched_value = CachedSortedVersions(PypiPackageList('httpx'), 'httpx').as_list()
    def se(request: httpx.Request) -> None:
        raise AssertionError
    respx_mock.get('https://pypi.org/pypi/httpx/json').mock(side_effect=se)
    got = CachedSortedVersions(PypiPackageList('httpx'), 'httpx').as_list()

    assert len(list(other_dir.glob('**/*'))) == 3
    assert other_dir / '.deltaver_cache/httpx/2024-02-05.json' in other_dir.glob('**/*')
    assert got == http_fetched_value


def test_remove_old_cache(exist_cache: Path, time_machine: TimeMachineFixture, respx_mock: MockRouter) -> None:
    """Test remove old cache."""
    time_machine.move_to(datetime.datetime(2024, 2, 6, tzinfo=datetime.timezone.utc))
    CachedSortedVersions(PypiPackageList('httpx'), 'httpx').as_list()
    def se(request: httpx.Request) -> None:
        raise AssertionError
    respx_mock.get('https://pypi.org/pypi/httpx/json').mock(side_effect=se)
    CachedSortedVersions(PypiPackageList('httpx'), 'httpx').as_list()

    assert len(list(exist_cache.glob('**/*'))) == 3
    assert exist_cache / '.deltaver_cache/httpx/2024-02-05.json' not in exist_cache.glob('**/*')
    assert exist_cache / '.deltaver_cache/httpx/2024-02-06.json' in exist_cache.glob('**/*')


@pytest.mark.usefixtures('_mock_vue')
def test_npm_versions() -> None:
    """Test NpmjsVersionsSortedBySemver."""
    got = NpmjsVersionsSortedBySemver('https://registry.npmjs.org', 'vue').fetch()

    assert len(got) == 278
    assert got[0] == {'0.0.0': datetime.date(2013, 12, 7)}
    assert got[-1] == {'3.4.20': datetime.date(2024, 2, 26)}
    assert got[148] == {'2.6.3': datetime.date(2019, 2, 6)}
