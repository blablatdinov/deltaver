from pathlib import Path

import pytest
from httpx import Response
from respx.router import MockRouter
from time_machine import TimeMachineFixture

from deltaver.version_delta import PypiVersionDelta, VersionNotFoundError, VersionsSortedByDate, VersionsSortedBySemver


@pytest.fixture()
def _mock_pypi(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/httpx/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/httpx_pypi_response.json').read_text(),
    ))


@pytest.fixture()
def _mock_eljson(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/eljson/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/eljson_response.json').read_text(),
    ))


@pytest.fixture()
def _mock_gitdb(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/gitdb/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/gitdb_response.json').read_text(),
    ))


@pytest.mark.usefixtures('_mock_pypi')
def test_previous(time_machine: TimeMachineFixture) -> None:
    # 0.25.1 was released 2023-11-03
    # 0.25.2 was released 2023-11-24
    time_machine.move_to('2023-12-20')
    assert PypiVersionDelta(VersionsSortedBySemver('httpx'), '0.25.1').days() == 25


@pytest.mark.usefixtures('_mock_pypi')
def test_last_version() -> None:
    assert PypiVersionDelta(VersionsSortedBySemver('httpx'), '0.25.2').days() == 0


@pytest.mark.usefixtures('_mock_pypi')
def test_fake_version() -> None:
    with pytest.raises(VersionNotFoundError):
        PypiVersionDelta(VersionsSortedBySemver('httpx'), '0.50.0').days()


@pytest.mark.usefixtures('_mock_eljson')
def test_eljson() -> None:
    assert PypiVersionDelta(VersionsSortedBySemver('eljson'), '0.0.1a1').days() == 0


@pytest.mark.usefixtures('_mock_gitdb')
def test_gitdb() -> None:
    assert PypiVersionDelta(VersionsSortedBySemver('gitdb'), '4.0.9').days() == 429


@pytest.mark.usefixtures('_mock_pypi')
def test_date_delta(time_machine) -> None:
    time_machine.move_to('2023-12-20')
    assert PypiVersionDelta(VersionsSortedByDate('httpx'), '0.25.1').days() == 25
