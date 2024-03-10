import datetime
from pathlib import Path

import pytest
from respx import MockRouter
from httpx import Response

from deltaver.pypi_package import PypiPackage


@pytest.fixture()
def _mock_httpx(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/httpx/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/httpx_pypi_response.json').read_text(),
    ))


@pytest.mark.usefixtures('_mock_httpx')
def test():
    got = PypiPackage('httpx', '0.25.0')

    assert got.release_date() == datetime.date(2023, 9, 11)
    assert got.next().release_date() == datetime.date(2023, 11, 3)
    assert got.next().next().release_date() == datetime.date(2023, 11, 24)
