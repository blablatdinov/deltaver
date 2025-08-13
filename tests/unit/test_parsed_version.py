# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import pytest

from deltaver.parsed_version import ParsedVersion


@pytest.mark.parametrize('version', [
    '1.0.0',
    '3.0.0-alpha9.5',
])
def test_correct(version: str) -> None:
    parsed_version = ParsedVersion(version)
    assert str(parsed_version.parse()) == version


def test_v_prefix() -> None:
    assert str(ParsedVersion('v2.0.0').parse()) == '2.0.0'


def test_dev() -> None:
    assert str(ParsedVersion('0.13.0.dev1').parse()) == '0.13.0-dev.1'


def test_compare() -> None:
    assert ParsedVersion('3.0.0-alpha9.5').parse() < ParsedVersion('3.0.0-alpha9.6').parse()