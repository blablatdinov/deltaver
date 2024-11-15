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

"""Unit test of entry."""

import datetime
import zipfile
from pathlib import Path

import httpx
import pytest
import respx
from time_machine import TimeMachineFixture

from deltaver.entry import logic
from deltaver.formats import Formats
from deltaver.parsed_requirements import PackageLockReqs


@pytest.fixture
def _mock_pypi(respx_mock: respx.router.MockRouter, tmp_path: Path) -> None:
    with zipfile.ZipFile('tests/fixtures/pypi_mock.zip', 'r') as zip_ref:
        zip_ref.extractall(tmp_path)
    for line in Path('tests/fixtures/requirements.txt').read_text().strip().splitlines():
        package_name = line.split('==')[0]
        respx_mock.get('https://pypi.org/pypi/{0}/json'.format(package_name)).mock(
            return_value=httpx.Response(
                200,
                text=Path(tmp_path / 'fixtures/{0}_pypi_response.json'.format(package_name)).read_text(),
            ),
        )


@pytest.fixture
def _mock_npmjs(respx_mock: respx.router.MockRouter, tmp_path: Path) -> None:
    with zipfile.ZipFile('tests/fixtures/npm_mock.zip', 'r') as zip_ref:
        zip_ref.extractall(tmp_path)
    for package_name, _ in PackageLockReqs(Path('tests/fixtures/package-lock-example.json').read_text()).reqs():
        respx_mock.get('https://registry.npmjs.org/{0}'.format(package_name)).mock(return_value=httpx.Response(
            200,
            text=Path(tmp_path / 'npm/{0}.json'.format(package_name)).read_text(),
        ))


@pytest.mark.usefixtures('_mock_pypi')
@pytest.mark.slow  # TODO: optimize
def test(time_machine: TimeMachineFixture) -> None:  # noqa: WPS210. TODO: fix
    """Test logic function."""
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    packages, sum_delta, max_delta = logic(
        Path('tests/fixtures/requirements.txt').read_text(),
        [],
        Formats.pip_freeze,
    )

    assert [
        (name, version, delta)
        for name, version, delta in packages
        if delta > 0
    ] == [
        ('SQLAlchemy', '1.4.51', 366),
        ('jsonschema', '4.21.0', 8),
        ('MarkupSafe', '2.1.3', 8),
        ('diff_cover', '8.0.2', 7),
        ('bandit', '1.7.6', 4),
        ('cryptography', '41.0.7', 4),
        ('pluggy', '1.3.0', 3),
        ('refurb', '1.27.0', 3),
    ]
    assert sum_delta == 403
    assert max_delta == 366


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
@pytest.mark.slow  # TODO: optimize
def test_excluded(time_machine: TimeMachineFixture) -> None:  # noqa: WPS210. TODO: fix
    """Test excluded param."""
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    packages, sum_delta, max_delta = logic(
        Path('tests/fixtures/requirements.txt').read_text(),
        ['sqlalchemy', 'bandit'],
        Formats.pip_freeze,
    )

    assert [
        (name, version, delta)
        for name, version, delta in packages
        if delta > 0
    ] == [
        ('jsonschema', '4.21.0', 8),
        ('MarkupSafe', '2.1.3', 8),
        ('diff_cover', '8.0.2', 7),
        ('cryptography', '41.0.7', 4),
        ('pluggy', '1.3.0', 3),
        ('refurb', '1.27.0', 3),
    ]
    assert sum_delta == 33
    assert max_delta == 8


@pytest.mark.usefixtures('_mock_npmjs')
@pytest.mark.slow
def test_package_lock(time_machine: TimeMachineFixture) -> None:  # noqa: WPS210. TODO
    """Test npmjs."""
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    packages, sum_delta, max_delta = logic(
        Path('tests/fixtures/package-lock-example.json').read_text(),
        [],
        Formats.npm_lock,
    )

    assert [
        (name, version, delta)
        for name, version, delta in packages
        if delta > 0
    ] == [
        ('immediate', '3.0.6', 3201),
        ('isarray', '0.0.1', 2970),
        ('is-arrayish', '0.2.1', 2926),
        ('path-to-regexp', '1.8.0', 2348),
        ('resolve-from', '3.0.0', 2317),
        ('commander', '2.11.0', 2257),
        ('decamelize', '1.2.0', 2210),
        ('load-json-file', '4.0.0', 2092),
        ('read-pkg-up', '3.0.0', 2049),
        ('read-pkg', '3.0.0', 2042),
        ('map-obj', '2.0.0', 1998),
        ('pify', '3.0.0', 1997),
        ('readable-stream', '2.3.8', 1996),
        ('color-name', '1.1.3', 1954),
        ('camelcase-keys', '4.2.0', 1929),
        ('path-is-absolute', '1.0.1', 1906),
        ('quick-lru', '1.1.0', 1903),
        ('string_decoder', '1.1.1', 1887),
        ('remove-array-items', '1.1.1', 1871),
        ('minimist-options', '3.0.2', 1840),
        ('nanoassert', '1.1.0', 1832),
        ('color-convert', '1.9.3', 1822),
        ('p-locate', '3.0.0', 1782),
        ('path-type', '3.0.0', 1782),
        ('pkg-dir', '3.0.0', 1782),
        ('loud-rejection', '1.6.0', 1776),
        ('path-exists', '3.0.0', 1759),
        ('arrify', '1.0.1', 1758),
        ('has-flag', '3.0.0', 1757),
        ('locate-path', '3.0.0', 1748),
        ('escape-string-regexp', '1.0.5', 1746),
        ('indent-string', '3.2.0', 1746),
        ('strip-indent', '2.0.0', 1746),
        ('is-obj', '1.0.1', 1744),
        ('is-plain-obj', '1.1.0', 1743),
        ('redent', '2.0.0', 1737),
        ('strip-bom', '3.0.0', 1735),
        ('trim-newlines', '2.0.0', 1734),
        ('resolve-cwd', '2.0.0', 1733),
        ('glob', '7.1.3', 1725),
        ('find-up', '3.0.0', 1721),
        ('ansi-styles', '3.2.1', 1702),
        ('import-local', '2.0.0', 1673),
        ('parse-json', '4.0.0', 1670),
        ('hosted-git-info', '2.8.9', 1629),
        ('rimraf', '2.7.1', 1627),
        ('chrome-launcher', '0.11.2', 1550),
        ('chalk', '2.4.2', 1540),
        ('meow', '5.0.0', 1512),
        ('emoji-regex', '8.0.0', 1387),
        ('@types/node', '13.13.2', 1371),
        ('chrome-remote-interface', '0.28.1', 1371),
        ('graceful-fs', '4.2.3', 1369),
        ('is-wsl', '2.1.1', 1364),
        ('spdx-expression-parse', '3.0.0', 1354),
        ('spdx-correct', '3.1.0', 1345),
        ('p-limit', '2.3.0', 1330),
        ('binary-extensions', '2.0.0', 1309),
        ('loglevel', '1.6.8', 1249),
        ('spdx-license-ids', '3.0.5', 1228),
        ('brace-expansion', '1.1.11', 1209),
        ('normalize-package-data', '2.5.0', 1201),
        ('resolve', '1.17.0', 1195),
        ('pako', '1.0.11', 1166),
        ('supports-color', '7.2.0', 1159),
        ('ms', '2.1.2', 1145),
        ('@sinonjs/fake-timers', '6.0.1', 1110),
        ('nanobus', '4.4.0', 1073),
        ('nise', '4.0.4', 1071),
        ('sinon', '9.2.4', 1041),
        ('@sinonjs/samsam', '5.3.1', 1033),
        ('just-extend', '4.1.1', 1028),
        ('balanced-match', '1.0.0', 1026),
        ('@sinonjs/commons', '1.8.2', 1024),
        ('picomatch', '2.2.2', 1022),
        ('ansi-regex', '5.0.1', 1016),
        ('is-fullwidth-code-point', '3.0.0', 1016),
        ('string-width', '4.2.3', 1016),
        ('strip-ansi', '6.0.1', 1016),
        ('wrap-ansi', '7.0.0', 1016),
        ('is-unicode-supported', '0.1.0', 1014),
        ('log-symbols', '4.1.0', 1014),
        ('marky', '1.2.1', 1001),
        ('fs-extra', '9.1.0', 999),
        ('glob-parent', '5.1.2', 999),
        ('lighthouse-logger', '1.2.0', 921),
        ('yocto-queue', '0.1.0', 898),
        ('strip-json-comments', '3.1.1', 891),
        ('signal-exit', '3.0.3', 864),
        ('is-glob', '4.0.1', 853),
        ('p-try', '2.2.0', 845),
        ('assertion-error', '1.1.0', 844),
        ('minimatch', '3.0.4', 720),
        ('debug', '4.3.3', 681),
        ('nanoid', '3.3.1', 670),
        ('workerpool', '6.2.0', 656),
        ('mocha', '9.2.2', 636),
        ('ansi-colors', '4.1.1', 622),
        ('diff', '5.0.0', 614),
        ('camelcase', '6.3.0', 600),
        ('@sinonjs/text-encoding', '0.7.1', 549),
        ('cliui', '7.0.4', 484),
        ('concat-map', '0.0.1', 472),
        ('decamelize-keys', '1.1.0', 454),
        ('which', '2.0.2', 452),
        ('serialize-javascript', '6.0.0', 377),
        ('typescript', '4.9.5', 317),
        ('selenium-webdriver', '4.8.2', 281),
        ('semver', '5.7.1', 201),
        ('pathval', '1.1.1', 190),
        ('isexe', '2.0.0', 181),
        ('chai', '4.3.7', 156),
        ('mock-socket', '9.2.1', 144),
        ('flat', '5.0.2', 134),
        ('get-func-name', '2.0.0', 123),
        ('check-error', '1.0.2', 122),
        ('loupe', '2.3.6', 106),
        ('deep-eql', '4.1.3', 101),
        ('universalify', '2.0.0', 87),
        ('chai-dom', '1.11.0', 74),
        ('ws', '8.14.2', 49),
        ('spdx-exceptions', '2.3.0', 3),
    ]
    assert sum_delta == 151154
    assert max_delta == 3201
