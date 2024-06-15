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

"""Python project designed to calculate the lag or delay in dependencies in terms of days."""

from enum import Enum
from pathlib import Path

import typer
from rich import print as rich_print

app = typer.Typer()


class Formats(Enum):
    """Dependencies file format."""

    pip_freeze = 'pip-freeze'
    poetry_lock = 'poetry-lock'
    npm_lock = 'npm-lock'


@app.command()
def main(
    path_to_file: Path = typer.Argument(help='\n\n'.join([  # noqa: B008, WPS404. Typer API
        'Path to file which specified project dependencies.',
        'Examples:',
        ' - requirements.txt',
        ' - ./poetry.lock',
        ' - /home/user/code/deltaver/poetry.lock',
    ])),
    file_format: Formats = typer.Option(  # noqa: B008, WPS404. Typer API
        Formats.pip_freeze.value,
        '--format',
        help='Dependencies file format',
    ),
) -> None:
    """Python project designed to calculate the lag or delay in dependencies in terms of days."""
    rich_print('Content length: {0}'.format(len(path_to_file.read_text())))
    rich_print('Format: {0}'.format(file_format))
