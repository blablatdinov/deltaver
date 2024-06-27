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

"""Integration test with installing."""

import os
import re
import subprocess
from collections.abc import Generator
from pathlib import Path

import pytest
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


@pytest.mark.usefixtures('_tmp_directory')
def test(current_dir: Path) -> None:
    """Test run command."""
    got = subprocess.run(
        ['venv/bin/deltaver_new', str(current_dir / 'tests/fixtures/requirements.txt')],
        stdout=subprocess.PIPE,
        check=False,
    )
    stdout = got.stdout.decode('utf-8').strip().splitlines()

    assert got.returncode == 0, got.stderr
    assert re.match(
        r'Content length: \d+',
        stdout[0],
    )
    assert stdout[1] == 'Format: Formats.pip_freeze'
