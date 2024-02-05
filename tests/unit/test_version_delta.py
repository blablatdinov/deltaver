import datetime
from pathlib import Path

import pytest
from httpx import Response
from respx.router import MockRouter
from time_machine import TimeMachineFixture

from deltaver.version_delta import (
    DecrDelta,
    FkVersionDelta,
    PypiVersionDelta,
    TargetGreaterLastError,
    VersionsSortedByDate,
    VersionsSortedBySemver,
    CachedSortedVersions,
    FkSortedVersions,
)


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


@pytest.fixture()
def _mock_greenlet(respx_mock: MockRouter) -> None:
    respx_mock.get('https://pypi.org/pypi/greenlet/json').mock(return_value=Response(
        200,
        text=Path('tests/fixtures/greenlet_response.json').read_text(),
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
    with pytest.raises(TargetGreaterLastError):
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


# @pytest.mark.usefixtures('_mock_cryptography')
def test_atomicwrites(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 28, tzinfo=datetime.timezone.utc))
    assert PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'atomicwrites'), '1.4.0').days() == 569


@pytest.mark.usefixtures('_mock_pypi')
def test_target_greater_than_last(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2023, 12, 19, tzinfo=datetime.timezone.utc))
    with pytest.raises(TargetGreaterLastError):
        PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'httpx'), '0.27.0').days()


@pytest.mark.usefixtures('_mock_greenlet')
def test_release_candidate(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2023, 12, 19, tzinfo=datetime.timezone.utc))
    PypiVersionDelta(VersionsSortedBySemver('https://pypi.org/', 'greenlet'), '3.0.0rc3').days()


def test_decr_delta(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 2, 5, tzinfo=datetime.timezone.utc))
    got = DecrDelta(
        FkVersionDelta(15),
        datetime.datetime(2024, 2, 1, tzinfo=datetime.timezone.utc).date(),
    ).days()

    assert got == 11


def test_negative_decr_delta(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 2, 5, tzinfo=datetime.timezone.utc))
    got = DecrDelta(
        FkVersionDelta(15),
        datetime.datetime(2020, 2, 1, tzinfo=datetime.timezone.utc).date(),
    ).days()

    assert got == 0


@pytest.mark.usefixtures('_mock_pypi')
def test_cached_version_delta():
    CachedSortedVersions(FkSortedVersions(

    ))
