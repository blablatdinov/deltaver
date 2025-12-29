# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Dependencies file format."""

from enum import Enum


class Formats(Enum):
    """Dependencies file format."""

    pip_freeze = 'pip-freeze'
    poetry_lock = 'poetry-lock'
    npm_lock = 'npm-lock'
    golang = 'golang'
    mix_lock = 'mix-lock'

    default = 'default'
