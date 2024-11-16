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

import os
from pathlib import Path

import pytest

from deltaver.entry import config_ctor, config_from_cli, pyproject_config
from deltaver.formats import Formats


@pytest.fixture
def _tmp_directory(tmpdir_factory):
    current = Path().absolute()
    tmp_path = tmpdir_factory.mktemp('test')
    os.chdir(tmp_path)
    yield
    os.chdir(current)


# @pytest.mark.usefixtures('_tmp_directory')
def test_cli_only():
    got = config_ctor(
        config_from_cli(
            '', Formats.default, -1, -1,
        ),
        {},
    )

    assert got == {
        'excluded': [],
        'fail_on_avg': -1,
        'fail_on_max': -1,
        'file_format': Formats.pip_freeze,
        'path_to_file': '',
    }


def test_with_pyproject():
    got = config_ctor(
        config_from_cli(
            '', Formats.default, -1, -1,
        ),
        {},
    )
