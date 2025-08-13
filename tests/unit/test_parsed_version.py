"""Unit tests for parsed version module."""

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
    """Test correct version parsing."""
    parsed_version = ParsedVersion(version)
    assert str(parsed_version.parse()) == version


def test_v_prefix() -> None:
    """Test version with v prefix."""
    assert str(ParsedVersion('v2.0.0').parse()) == '2.0.0'


def test_dev() -> None:
    """Test dev version parsing."""
    assert str(ParsedVersion('0.13.0.dev1').parse()) == '0.13.0-dev1'
    assert str(ParsedVersion('0.13.dev0').parse()) == '0.13.0-dev0'


def test_alpha() -> None:
    """Test alpha version parsing."""
    assert str(ParsedVersion('1.0.0a').parse()) == '1.0.0-a'


def test_beta() -> None:
    """Test beta version parsing."""
    assert str(ParsedVersion('0.15.0b1').parse()) == '0.15.0-b1'
    assert str(ParsedVersion('0.15.0-b1').parse()) == '0.15.0-b1'


def test_rc() -> None:
    """Test rc version parsing."""
    assert str(ParsedVersion('0.15.0rc1').parse()) == '0.15.0-rc1'


def test_post_release() -> None:
    """Test post release version parsing."""
    assert str(ParsedVersion('4.6.2.post1').parse()) == '4.6.2+post1'


def test_zero_before_int() -> None:
    """Test zero before int."""
    assert str(ParsedVersion('14.05.14').parse()) == '14.5.14'


def test_compare() -> None:
    """Test version comparison."""
    assert ParsedVersion('3.0.0-alpha9.5').parse() < ParsedVersion('3.0.0-alpha9.6').parse()
