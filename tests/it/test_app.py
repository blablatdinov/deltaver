import re
from pathlib import Path

import pytest
import respx
from httpx import Response
from typer.testing import CliRunner

from deltaver.__main__ import app


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def _mock_pypi(respx_mock: respx.router.MockRouter) -> None:
    for line in Path('tests/fixtures/requirements.txt').read_text().strip().splitlines():
        package_name = line.split('==')[0]
        respx_mock.get('https://pypi.org/pypi/{0}/json'.format(package_name)).mock(return_value=Response(
            200,
            text=Path('tests/fixtures/{0}_pypi_response.json'.format(package_name)).read_text(),
        ))


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test(runner: CliRunner) -> None:
    got = runner.invoke(app, ['tests/fixtures/requirements.txt'])

    assert got.exit_code == 0
    assert re.match(
        r'Scanning... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% \d:\d{2}:\d{2}',
        got.stdout.splitlines()[0],
    )
    assert got.stdout.splitlines()[1:-1] == [
        '┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┓',
        '┃ Package      ┃ Version ┃ Delta (days) ┃',
        '┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━┩',
        '│ SQLAlchemy   │ 1.4.51  │ 1024         │',
        '│ smmap        │ 5.0.1   │ 130          │',
        '│ jsonschema   │ 4.21.0  │ 6            │',
        '│ MarkupSafe   │ 2.1.3   │ 6            │',
        '│ diff_cover   │ 8.0.2   │ 5            │',
        '│ cryptography │ 41.0.7  │ 3            │',
        '│ bandit       │ 1.7.6   │ 2            │',
        '│ pluggy       │ 1.3.0   │ 1            │',
        '│ refurb       │ 1.27.0  │ 1            │',
        '└──────────────┴─────────┴──────────────┘',
    ]
    assert got.stdout.splitlines()[-1] == 'Average delta: 8.66'
