import respx
from pathlib import Path
from httpx import Response

from deltaver.version_delta import PypiVersionDelta


@respx.mock
def test_previous(time_machine):
    # 0.25.1 was released 2023-11-03
    # 0.25.2 was released 2023-11-24
    time_machine.move_to('2023-12-20')
    respx.get('https://pypi.org/pypi/httpx/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/httpx_pypi_response.json').read_text(),
    ))
    assert PypiVersionDelta('httpx', '0.25.1').days() == 26


@respx.mock
def test_last_version():
    respx.get('https://pypi.org/pypi/httpx/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/httpx_pypi_response.json').read_text(),
    ))
    assert PypiVersionDelta('httpx', '0.25.2').days() == 0
