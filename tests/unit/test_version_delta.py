import datetime
from pathlib import Path
from typing import final

import attrs
import pytest
from httpx import Response
from respx.router import MockRouter
from time_machine import TimeMachineFixture

from deltaver.version_delta import (
    PypiVersionDelta,
    TailLossDateVersions,
    VersionDelta,
    VersionNotFoundError,
    VersionsSortedByDate,
    VersionsSortedBySemver,
)


@final
@attrs.define(frozen=True)
class FkVersionDelta(VersionDelta):

    _value: list

    def fetch(self) -> list:
        return self._value


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


@pytest.fixture()
def _mock_cryptography(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/cryptography/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/cryptography_response.json').read_text(),
    ))


@pytest.mark.usefixtures('_mock_pypi')
def test_previous(time_machine: TimeMachineFixture) -> None:
    # 0.25.1 was released 2023-11-03
    # 0.25.2 was released 2023-11-24
    time_machine.move_to(datetime.datetime(2023, 12, 19, tzinfo=datetime.timezone.utc))
    assert PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'httpx'), '0.25.1').days() == 25


@pytest.mark.usefixtures('_mock_pypi')
def test_last_version() -> None:
    assert PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'httpx'), '0.25.2').days() == 0


@pytest.mark.usefixtures('_mock_pypi')
def test_fake_version() -> None:
    with pytest.raises(VersionNotFoundError):
        PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'httpx'), '0.50.0').days()


@pytest.mark.usefixtures('_mock_eljson')
def test_eljson() -> None:
    assert PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'eljson'), '0.0.1a1').days() == 0


@pytest.mark.usefixtures('_mock_gitdb')
def test_gitdb(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    assert PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'gitdb'), '4.0.9').days() == 429


@pytest.mark.usefixtures('_mock_pypi')
def test_date_delta(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2023, 12, 19, tzinfo=datetime.timezone.utc))
    assert PypiVersionDelta(VersionsSortedByDate('httpx'), '0.25.1').days() == 25


@pytest.mark.usefixtures('_mock_cryptography')
def test_cryptography(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 28, tzinfo=datetime.timezone.utc))
    assert PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'cryptography'), '42.0.1').days() == 0


def test_tail_loss_by_date() -> None:
    got = TailLossDateVersions(
        FkVersionDelta([
            {
                '0.1.0': [
                    {'upload_time': '2019-07-19T14:23:35'},
                ],
            },
            {
                '0.2.0': [
                    {'upload_time': '2020-07-19T14:23:35'},
                ],
            },
        ]),
        datetime.date(2020, 5, 1),
    ).fetch()

    assert got == [{'0.1.0': [{'upload_time': '2019-07-19T14:23:35'}]}]


def test_tail_loss_by_date_null_version_info() -> None:
    TailLossDateVersions(
        FkVersionDelta([
            {
                '0.0.1': [],
            },
        ]),
        datetime.date(2020, 5, 1),
    ).fetch()
