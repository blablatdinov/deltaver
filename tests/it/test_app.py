import datetime
import os
import re
import zipfile
from collections.abc import Generator
from pathlib import Path
from shutil import copyfile

import pytest
import respx
from httpx import Response
from time_machine import TimeMachineFixture
from typer.testing import CliRunner

from deltaver.__main__ import app
from deltaver.parsed_requirements import PackageLockReqs


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def _mock_pypi(respx_mock: respx.router.MockRouter, tmp_path: Path) -> None:
    with zipfile.ZipFile('tests/fixtures/pypi_mock.zip', 'r') as zip_ref:
        zip_ref.extractall(tmp_path)
    for line in Path('tests/fixtures/requirements.txt').read_text().strip().splitlines():
        package_name = line.split('==')[0]
        respx_mock.get('https://pypi.org/pypi/{0}/json'.format(package_name)).mock(return_value=Response(
            200,
            text=Path(tmp_path / 'fixtures/{0}_pypi_response.json'.format(package_name)).read_text(),
        ))


@pytest.fixture()
def _mock_npmjs(respx_mock: respx.router.MockRouter, tmp_path: Path) -> None:
    with zipfile.ZipFile('tests/fixtures/npm_mock.zip', 'r') as zip_ref:
        zip_ref.extractall(tmp_path)
    for package_name, _ in PackageLockReqs(Path('tests/fixtures/package-lock-example.json')).reqs():
        respx_mock.get('https://registry.npmjs.org/immediate/{0}'.format(package_name)).mock(return_value=Response(
            200,
            text=Path(tmp_path / 'npm/{0}.json'.format(package_name)).read_text(),
        ))


@pytest.fixture()
def latest_requirements_file(tmp_path: Path) -> Path:
    path = (tmp_path / 'requirements.txt')
    path.write_text('httpx==0.26.0')
    return path


@pytest.fixture()
def _other_dir(tmp_path: Path) -> Generator[None, None, None]:
    origin_dir = Path.cwd()
    copyfile('tests/fixtures/pyproject.toml', tmp_path / 'pyproject.toml')
    copyfile('tests/fixtures/requirements.txt', tmp_path / 'requirements.txt')
    os.chdir(tmp_path)
    yield
    os.chdir(origin_dir)


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test(runner: CliRunner, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    got = runner.invoke(app, ['tests/fixtures/requirements.txt'])

    assert got.exit_code == 0, got.stdout
    assert re.match(
        r'Scanning... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% \d:\d{2}:\d{2}',
        got.stdout.splitlines()[0],
    )
    assert got.stdout.splitlines()[1:] == [
        '┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓',
        '┃ Package      ┃ Version ┃ Delta (days) ┃',
        '┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩',
        '│ SQLAlchemy   │ 1.4.51  │ 366          │',
        '│ smmap        │ 5.0.1   │ 132          │',
        '│ jsonschema   │ 4.21.0  │ 8            │',
        '│ MarkupSafe   │ 2.1.3   │ 8            │',
        '│ diff_cover   │ 8.0.2   │ 7            │',
        '│ bandit       │ 1.7.6   │ 4            │',
        '│ cryptography │ 41.0.7  │ 4            │',
        '│ pluggy       │ 1.3.0   │ 3            │',
        '│ refurb       │ 1.27.0  │ 3            │',
        '└──────────────┴─────────┴──────────────┘',
        'Max delta: 366',
        'Average delta: 3.93',
    ]


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test_fail_by_average(runner: CliRunner) -> None:
    got = runner.invoke(app, ['tests/fixtures/requirements.txt', '--fail-on-avg', '1'])

    assert got.exit_code == 1, got.stdout
    assert got.stdout.splitlines()[-2:] == ['', 'Error: average delta greater than available']


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test_fail_by_max(runner: CliRunner) -> None:
    got = runner.invoke(app, ['tests/fixtures/requirements.txt', '--fail-on-max', '1'])

    assert got.exit_code == 1, got.stdout
    assert got.stdout.splitlines()[-2:] == ['', 'Error: max delta greater than available']


@pytest.mark.usefixtures('_mock_pypi')
def test_zero_delta(latest_requirements_file: Path, runner: CliRunner) -> None:
    got = runner.invoke(app, [str(latest_requirements_file)])

    assert got.exit_code == 0, got.stdout
    assert got.stdout.splitlines()[-2] == 'Max delta: 0'
    assert got.stdout.splitlines()[-1] == 'Average delta: 0.00'


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test_excluded(runner: CliRunner, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    got = runner.invoke(app, ['tests/fixtures/requirements.txt', '--exclude', 'sqlalchemy', '--exclude', 'bandit'])

    assert got.exit_code == 0, got.stdout
    assert re.match(
        r'Scanning... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% \d:\d{2}:\d{2}',
        got.stdout.splitlines()[0],
    )
    assert got.stdout.splitlines()[1:] == [
        '┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓',
        '┃ Package      ┃ Version ┃ Delta (days) ┃',
        '┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩',
        '│ smmap        │ 5.0.1   │ 132          │',
        '│ jsonschema   │ 4.21.0  │ 8            │',
        '│ MarkupSafe   │ 2.1.3   │ 8            │',
        '│ diff_cover   │ 8.0.2   │ 7            │',
        '│ cryptography │ 41.0.7  │ 4            │',
        '│ pluggy       │ 1.3.0   │ 3            │',
        '│ refurb       │ 1.27.0  │ 3            │',
        '└──────────────┴─────────┴──────────────┘',
        'Max delta: 132',
        'Average delta: 1.23',
    ]


@pytest.mark.usefixtures('_mock_pypi', '_other_dir')
@respx.mock(assert_all_mocked=False)
def test_parse_pyproject_toml(runner: CliRunner, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    got = runner.invoke(app, ['requirements.txt'])

    assert got.exit_code == 1, got.stdout
    assert got.stdout.splitlines()[1:] == [
        '┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓',
        '┃ Package      ┃ Version ┃ Delta (days) ┃',
        '┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩',
        '│ smmap        │ 5.0.1   │ 132          │',
        '│ jsonschema   │ 4.21.0  │ 8            │',
        '│ MarkupSafe   │ 2.1.3   │ 8            │',
        '│ diff_cover   │ 8.0.2   │ 7            │',
        '│ bandit       │ 1.7.6   │ 4            │',
        '│ cryptography │ 41.0.7  │ 4            │',
        '│ pluggy       │ 1.3.0   │ 3            │',
        '│ refurb       │ 1.27.0  │ 3            │',
        '└──────────────┴─────────┴──────────────┘',
        'Max delta: 132',
        'Average delta: 1.25',
        '',
        'Error: average delta greater than available',
    ]


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test_for_date_arg(runner: CliRunner, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    got = runner.invoke(app, ['tests/fixtures/requirements.txt', '--for-date', '2024-01-26'])

    assert got.exit_code == 0, got.stdout
    assert re.match(
        r'Scanning... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% \d:\d{2}:\d{2}',
        got.stdout.splitlines()[0],
    )
    assert got.stdout.splitlines()[1:] == [
        '┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓',
        '┃ Package      ┃ Version ┃ Delta (days) ┃',
        '┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩',
        '│ SQLAlchemy   │ 1.4.51  │ 365          │',
        '│ smmap        │ 5.0.1   │ 131          │',
        '│ jsonschema   │ 4.21.0  │ 7            │',
        '│ MarkupSafe   │ 2.1.3   │ 7            │',
        '│ diff_cover   │ 8.0.2   │ 6            │',
        '│ bandit       │ 1.7.6   │ 3            │',
        '│ cryptography │ 41.0.7  │ 3            │',
        '│ pluggy       │ 1.3.0   │ 2            │',
        '│ refurb       │ 1.27.0  │ 2            │',
        '└──────────────┴─────────┴──────────────┘',
        'Max delta: 365',
        'Average delta: 3.87',
    ]


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test_for_date_arg_overtaking(runner: CliRunner, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    got = runner.invoke(app, ['tests/fixtures/requirements.txt', '--for-date', '2020-01-01'])

    assert got.exit_code == 0, got.stdout
    assert got.stdout.splitlines()[1:] == [
        '┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓',
        '┃ Package ┃ Version ┃ Delta (days) ┃',
        '┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩',
        '└─────────┴─────────┴──────────────┘',
        'Max delta: 0',
        'Average delta: 0.00',
    ]


@pytest.mark.usefixtures('_mock_npmjs')
@respx.mock(assert_all_mocked=False)
def test_js_project(runner: CliRunner, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 2, 26, tzinfo=datetime.timezone.utc))
    got = runner.invoke(app, ['tests/fixtures/package-lock-example.json', '--format', 'lock', '--lang', 'js'])

    assert got.exit_code == 0, got.stdout
    assert got.stdout.splitlines()[1:] == [
        '┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓',
        '┃ Package                 ┃ Version ┃ Delta (days) ┃',
        '┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩',
        '│ immediate               │ 3.0.6   │ 3231         │',
        '│ isarray                 │ 0.0.1   │ 3000         │',
        '│ is-arrayish             │ 0.2.1   │ 2956         │',
        '│ path-to-regexp          │ 1.8.0   │ 2378         │',
        '│ resolve-from            │ 3.0.0   │ 2347         │',
        '│ commander               │ 2.11.0  │ 2287         │',
        '│ decamelize              │ 1.2.0   │ 2240         │',
        '│ load-json-file          │ 4.0.0   │ 2122         │',
        '│ read-pkg-up             │ 3.0.0   │ 2079         │',
        '│ read-pkg                │ 3.0.0   │ 2072         │',
        '│ map-obj                 │ 2.0.0   │ 2028         │',
        '│ pify                    │ 3.0.0   │ 2027         │',
        '│ readable-stream         │ 2.3.8   │ 2026         │',
        '│ color-name              │ 1.1.3   │ 1984         │',
        '│ camelcase-keys          │ 4.2.0   │ 1959         │',
        '│ path-is-absolute        │ 1.0.1   │ 1936         │',
        '│ quick-lru               │ 1.1.0   │ 1933         │',
        '│ string_decoder          │ 1.1.1   │ 1917         │',
        '│ remove-array-items      │ 1.1.1   │ 1901         │',
        '│ minimist-options        │ 3.0.2   │ 1870         │',
        '│ nanoassert              │ 1.1.0   │ 1862         │',
        '│ color-convert           │ 1.9.3   │ 1852         │',
        '│ p-locate                │ 3.0.0   │ 1812         │',
        '│ path-type               │ 3.0.0   │ 1812         │',
        '│ pkg-dir                 │ 3.0.0   │ 1812         │',
        '│ loud-rejection          │ 1.6.0   │ 1806         │',
        '│ path-exists             │ 3.0.0   │ 1789         │',
        '│ arrify                  │ 1.0.1   │ 1788         │',
        '│ has-flag                │ 3.0.0   │ 1787         │',
        '│ locate-path             │ 3.0.0   │ 1778         │',
        '│ escape-string-regexp    │ 1.0.5   │ 1776         │',
        '│ indent-string           │ 3.2.0   │ 1776         │',
        '│ strip-indent            │ 2.0.0   │ 1776         │',
        '│ is-obj                  │ 1.0.1   │ 1774         │',
        '│ is-plain-obj            │ 1.1.0   │ 1773         │',
        '│ redent                  │ 2.0.0   │ 1767         │',
        '│ strip-bom               │ 3.0.0   │ 1765         │',
        '│ trim-newlines           │ 2.0.0   │ 1764         │',
        '│ resolve-cwd             │ 2.0.0   │ 1763         │',
        '│ glob                    │ 7.1.3   │ 1755         │',
        '│ find-up                 │ 3.0.0   │ 1751         │',
        '│ ansi-styles             │ 3.2.1   │ 1732         │',
        '│ import-local            │ 2.0.0   │ 1703         │',
        '│ parse-json              │ 4.0.0   │ 1700         │',
        '│ hosted-git-info         │ 2.8.9   │ 1659         │',
        '│ rimraf                  │ 2.7.1   │ 1657         │',
        '│ chrome-launcher         │ 0.11.2  │ 1580         │',
        '│ chalk                   │ 2.4.2   │ 1570         │',
        '│ meow                    │ 5.0.0   │ 1542         │',
        '│ emoji-regex             │ 8.0.0   │ 1417         │',
        '│ @types/node             │ 13.13.2 │ 1401         │',
        '│ chrome-remote-interface │ 0.28.1  │ 1401         │',
        '│ graceful-fs             │ 4.2.3   │ 1399         │',
        '│ is-wsl                  │ 2.1.1   │ 1394         │',
        '│ spdx-expression-parse   │ 3.0.0   │ 1384         │',
        '│ spdx-correct            │ 3.1.0   │ 1375         │',
        '│ p-limit                 │ 2.3.0   │ 1360         │',
        '│ binary-extensions       │ 2.0.0   │ 1339         │',
        '│ loglevel                │ 1.6.8   │ 1279         │',
        '│ spdx-license-ids        │ 3.0.5   │ 1258         │',
        '│ brace-expansion         │ 1.1.11  │ 1239         │',
        '│ normalize-package-data  │ 2.5.0   │ 1231         │',
        '│ resolve                 │ 1.17.0  │ 1225         │',
        '│ pako                    │ 1.0.11  │ 1196         │',
        '│ supports-color          │ 7.2.0   │ 1189         │',
        '│ ms                      │ 2.1.2   │ 1175         │',
        '│ @sinonjs/fake-timers    │ 6.0.1   │ 1140         │',
        '│ nanobus                 │ 4.4.0   │ 1103         │',
        '│ nise                    │ 4.0.4   │ 1101         │',
        '│ sinon                   │ 9.2.4   │ 1071         │',
        '│ @sinonjs/samsam         │ 5.3.1   │ 1063         │',
        '│ just-extend             │ 4.1.1   │ 1058         │',
        '│ balanced-match          │ 1.0.0   │ 1056         │',
        '│ @sinonjs/commons        │ 1.8.2   │ 1054         │',
        '│ picomatch               │ 2.2.2   │ 1052         │',
        '│ ansi-regex              │ 5.0.1   │ 1046         │',
        '│ is-fullwidth-code-point │ 3.0.0   │ 1046         │',
        '│ string-width            │ 4.2.3   │ 1046         │',
        '│ strip-ansi              │ 6.0.1   │ 1046         │',
        '│ wrap-ansi               │ 7.0.0   │ 1046         │',
        '│ is-unicode-supported    │ 0.1.0   │ 1044         │',
        '│ log-symbols             │ 4.1.0   │ 1044         │',
        '│ marky                   │ 1.2.1   │ 1031         │',
        '│ fs-extra                │ 9.1.0   │ 1029         │',
        '│ glob-parent             │ 5.1.2   │ 1029         │',
        '│ lighthouse-logger       │ 1.2.0   │ 951          │',
        '│ yocto-queue             │ 0.1.0   │ 928          │',
        '│ strip-json-comments     │ 3.1.1   │ 921          │',
        '│ signal-exit             │ 3.0.3   │ 894          │',
        '│ is-glob                 │ 4.0.1   │ 883          │',
        '│ p-try                   │ 2.2.0   │ 875          │',
        '│ assertion-error         │ 1.1.0   │ 874          │',
        '│ minimatch               │ 3.0.4   │ 750          │',
        '│ debug                   │ 4.3.3   │ 711          │',
        '│ nanoid                  │ 3.3.1   │ 700          │',
        '│ workerpool              │ 6.2.0   │ 686          │',
        '│ mocha                   │ 9.2.2   │ 666          │',
        '│ ansi-colors             │ 4.1.1   │ 652          │',
        '│ diff                    │ 5.0.0   │ 644          │',
        '│ camelcase               │ 6.3.0   │ 630          │',
        '│ @sinonjs/text-encoding  │ 0.7.1   │ 579          │',
        '│ cliui                   │ 7.0.4   │ 514          │',
        '│ concat-map              │ 0.0.1   │ 502          │',
        '│ decamelize-keys         │ 1.1.0   │ 484          │',
        '│ which                   │ 2.0.2   │ 482          │',
        '│ serialize-javascript    │ 6.0.0   │ 407          │',
        '│ typescript              │ 4.9.5   │ 347          │',
        '│ selenium-webdriver      │ 4.8.2   │ 311          │',
        '│ semver                  │ 5.7.1   │ 231          │',
        '│ pathval                 │ 1.1.1   │ 220          │',
        '│ isexe                   │ 2.0.0   │ 211          │',
        '│ chai                    │ 4.3.7   │ 186          │',
        '│ mock-socket             │ 9.2.1   │ 174          │',
        '│ flat                    │ 5.0.2   │ 164          │',
        '│ get-func-name           │ 2.0.0   │ 153          │',
        '│ check-error             │ 1.0.2   │ 152          │',
        '│ loupe                   │ 2.3.6   │ 136          │',
        '│ deep-eql                │ 4.1.3   │ 131          │',
        '│ universalify            │ 2.0.0   │ 117          │',
        '│ chai-dom                │ 1.11.0  │ 104          │',
        '│ ws                      │ 8.14.2  │ 79           │',
        '│ spdx-exceptions         │ 2.3.0   │ 33           │',
        '│ escalade                │ 3.1.1   │ 21           │',
        '└─────────────────────────┴─────────┴──────────────┘',
        'Max delta: 3231',
        'Average delta: 905.52',
    ]
