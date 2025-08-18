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

"""Integration test with installing."""

import os
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path
from shutil import copyfile

import pytest

if sys.version_info < (3, 11):
    import tomli as toml
else:
    import tomllib as toml

from _pytest.legacypath import TempdirFactory


@pytest.fixture(scope='module')
def current_dir() -> Path:
    """Current directory for installing actual deltaver."""
    return Path().absolute()


# flake8: noqa: S603, S607. Not a production code
@pytest.fixture(scope='module')
def _tmp_directory(tmpdir_factory: TempdirFactory, current_dir: str) -> Generator[None, None, None]:
    """Temporary directory for test."""
    tmp_path = tmpdir_factory.mktemp('test')
    os.chdir(tmp_path)
    subprocess.run(['python', '-m', 'venv', 'venv'], check=True)
    subprocess.run(['venv/bin/pip', 'install', 'pip', '-U'], check=True)
    subprocess.run(['venv/bin/pip', 'install', str(current_dir)], check=True)
    yield
    os.chdir(current_dir)


def _version_from_lock(package_name: str) -> str:
    return '{0}=={1}'.format(
        package_name,
        next(
            package
            for package in toml.loads(Path('poetry.lock').read_text(encoding='utf-8'))['package']
            if package['name'] == package_name
        )['version'],
    )


@pytest.mark.usefixtures('_tmp_directory')
def test(current_dir: Path) -> None:
    """Test run command."""
    Path('req.txt').write_text('httpx==0.25.0')
    got = subprocess.run(
        ['venv/bin/deltaver_new', 'req.txt'],
        stdout=subprocess.PIPE,
        check=False,
    )
    stdout = got.stdout.decode('utf-8').strip().splitlines()

    assert got.returncode == 0, got.stderr or stdout


@pytest.mark.usefixtures('_tmp_directory')
@pytest.mark.parametrize('version', [
    ('attrs==23.1.0',),
    (_version_from_lock('attrs'),),
    ('attrs', '-U'),

    ('httpx==0.24.0',),
    (_version_from_lock('httpx'),),
    ('httpx', '-U'),

    ('packaging==23.0',),
    (_version_from_lock('packaging'),),
    ('packaging', '-U'),

    ('typer==0.9.0',),
    (_version_from_lock('typer'),),
    ('typer', '-U'),

    ('rich==13.0.0',),
    (_version_from_lock('rich'),),
    ('rich', '-U'),

    ('toml==0.10.2',),
    (_version_from_lock('toml'),),
    ('toml', '-U'),

    ('pytz==2024.2',),
    (_version_from_lock('pytz'),),
    ('pytz', '-U'),

    ('typing-extensions==4.9.0',),
    (_version_from_lock('typing-extensions'),),
    ('typing-extensions', '-U'),
])
def test_versions(current_dir: Path, version: tuple[str, ...]) -> None:
    """Test run command."""
    subprocess.run(['venv/bin/pip', 'install', *version], check=True)
    Path('req.txt').write_text('httpx==0.25.0')
    got = subprocess.run(
        ['venv/bin/deltaver_new', 'req.txt'],
        stdout=subprocess.PIPE,
        check=False,
    )
    stdout = got.stdout.decode('utf-8').strip().splitlines()

    assert got.returncode == 0, got.stderr or stdout


@pytest.mark.usefixtures('_tmp_directory')
def test_fail_on_avg(current_dir: Path) -> None:
    """Test deltaver fail on average."""
    Path('req.txt').write_text('httpx==0.25.0')
    got = subprocess.run(
        ['venv/bin/deltaver_new', 'req.txt', '--fail-on-avg', '1'],
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.returncode == 1, (got.stderr or got.stdout).decode()


@pytest.mark.usefixtures('_tmp_directory')
def test_fail_on_max(current_dir: Path) -> None:
    """Test deltaver fail on max."""
    Path('req.txt').write_text('httpx==0.25.0')
    got = subprocess.run(
        ['venv/bin/deltaver_new', 'req.txt', '--fail-on-max', '1'],
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.returncode == 1, (got.stderr or got.stdout).decode()


@pytest.mark.usefixtures('_tmp_directory')
def test_poetry_lock(current_dir: Path) -> None:
    """Test poetry lock file."""
    copyfile((current_dir / 'tests/fixtures/poetry_lock_example.lock'), Path('poetry.lock'))
    got = subprocess.run(
        ['venv/bin/deltaver_new', 'poetry.lock', '--format', 'poetry-lock'],
        stdout=subprocess.PIPE,
        check=False,
    )
    stdout = got.stdout.decode('utf-8').strip().splitlines()

    assert got.returncode == 0, got.stderr or stdout


@pytest.mark.usefixtures('_tmp_directory')
def test_golang(current_dir: Path) -> None:
    """Test go.sum file."""
    copyfile((current_dir / 'tests/fixtures/go.sum'), Path('go.sum'))
    got = subprocess.run(
        ['venv/bin/deltaver_new', 'go.sum', '--format', 'golang'],
        stdout=subprocess.PIPE,
        check=False,
    )
    stdout = got.stdout.decode('utf-8').strip().splitlines()

    assert got.returncode == 0, got.stderr or stdout
