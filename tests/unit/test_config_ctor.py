# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test constructing deltaver config."""

from pathlib import Path

from deltaver._internal.config import PyprojectConfig
from deltaver.entry import config_ctor, config_from_cli
from deltaver._internal.formats import Formats


def test_cli_only() -> None:
    """Test cli only."""
    got = config_ctor(
        config_from_cli(
            Path(), Formats.default, -1, -1, [],
        ),
        PyprojectConfig({
            'excluded': [],
            'fail_on_avg': None,
            'fail_on_max': None,
            'file_format': None,
            'path_to_file': None,
        }),
    )

    assert got == {
        'excluded': [],
        'fail_on_avg': -1,
        'fail_on_max': -1,
        'file_format': Formats.pip_freeze,
        'path_to_file': Path(),
    }


def test_with_pyproject() -> None:
    """Test merge with pyproject."""
    got = config_ctor(
        config_from_cli(
            Path(), Formats.default, -1, -1, [],
        ),
        PyprojectConfig({
            'fail_on_avg': 40,
            'fail_on_max': 20,
            'excluded': [],
            'file_format': None,
            'path_to_file': None,
        }),
    )

    assert got == {
        'excluded': [],
        'fail_on_avg': 40,
        'fail_on_max': 20,
        'file_format': Formats.pip_freeze,
        'path_to_file': Path(),
    }


def test_fail_not_filled() -> None:
    """Test fail not filled."""
    got = config_ctor(
        config_from_cli(
            Path(), Formats.default, -1, -1, [],
        ),
        PyprojectConfig({
            'fail_on_avg': None,
            'fail_on_max': None,
            'excluded': [],
            'file_format': None,
            'path_to_file': None,
        }),
    )

    assert got == {
        'excluded': [],
        'fail_on_avg': -1,
        'fail_on_max': -1,
        'file_format': Formats.pip_freeze,
        'path_to_file': Path(),
    }
