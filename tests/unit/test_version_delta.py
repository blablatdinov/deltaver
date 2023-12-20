from pathlib import Path

import pytest
from httpx import Response
from respx.router import MockRouter
from time_machine import TimeMachineFixture

from deltaver.version_delta import PypiVersionDelta, VersionNotFoundError


@pytest.fixture()
def _mock_pypi(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/httpx/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/httpx_pypi_response.json').read_text(),
    ))


@pytest.mark.usefixtures('_mock_pypi')
def test_previous(time_machine: TimeMachineFixture) -> None:
    # 0.25.1 was released 2023-11-03
    # 0.25.2 was released 2023-11-24
    time_machine.move_to('2023-12-20')
    assert PypiVersionDelta('httpx', '0.25.1').days() == 25


@pytest.mark.usefixtures('_mock_pypi')
def test_last_version() -> None:
    assert PypiVersionDelta('httpx', '0.25.2').days() == 0


@pytest.mark.usefixtures('_mock_pypi')
def test_fake_version() -> None:
    with pytest.raises(VersionNotFoundError):
        PypiVersionDelta('httpx', '0.50.0').days()
