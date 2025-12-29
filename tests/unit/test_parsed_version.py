# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Unit tests for parsed version module."""

import pytest

from deltaver._internal.parsed_version import ParsedVersion


@pytest.mark.parametrize('version', [
    '1.0.0',
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
    assert str(ParsedVersion('0.13.0.dev1').parse()) == '0.13.0.dev1'
    assert str(ParsedVersion('0.13.dev0').parse()) == '0.13.dev0'


def test_beta() -> None:
    """Test beta version parsing."""
    assert str(ParsedVersion('0.15.0b1').parse()) == '0.15.0b1'
    assert str(ParsedVersion('0.15.0-b1').parse()) == '0.15.0b1'


def test_rc() -> None:
    """Test rc version parsing."""
    assert str(ParsedVersion('0.15.0rc1').parse()) == '0.15.0rc1'


def test_post_release() -> None:
    """Test post release version parsing."""
    assert str(ParsedVersion('4.6.2.post1').parse()) == '4.6.2.post1'


def test_zero_before_int() -> None:
    """Test zero before int."""
    assert str(ParsedVersion('14.05.14').parse()) == '14.5.14'


def test_four_char() -> None:
    """Test four char."""
    assert str(ParsedVersion('3.0.0.0').parse()) == '3.0.0.0'
