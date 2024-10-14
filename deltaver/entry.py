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

from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TypedDict

import pytz
import typer
from rich import print as rich_print
from rich.console import Console
from rich.progress import track
from rich.table import Table

from deltaver.delta import DaysDelta
from deltaver.package import CachedPackageList, FilteredPackageList, PypiPackageList, SortedPackageList
from deltaver.parsed_requirements import ExcludedReqs, FileNotFoundSafeReqs, FreezedReqs

app = typer.Typer()


class Formats(Enum):
    """Dependencies file format."""

    pip_freeze = 'pip-freeze'
    poetry_lock = 'poetry-lock'
    npm_lock = 'npm-lock'

    default = 'default'


class Config(TypedDict):
    """Config dict."""

    path_to_file: Path
    file_format: Formats
    excluded: list[str]
    fail_on_avg: int | None
    fail_on_max: int | None


@dataclass
class PackageOutLine:
    """DTO for package info."""

    name: str
    version: str
    delta: str


def config_ctor(
    path_to_file: Path,
    file_format: Formats,
    fail_on_avg: int | None,
    fail_on_max: int | None,
) -> Config:
    """Ctor for config."""
    config = {
        'path_to_file': path_to_file,
        'file_format': Formats.pip_freeze,
        'excluded': [],  # FIXME
        'fail_on_avg': fail_on_avg,
        'fail_on_max': fail_on_max,
    }
    if file_format == Formats.default:
        file_format = Formats.pip_freeze
    return config


def logic(
    requirements_file_content: str,
    excluded_reqs: str,
) -> tuple[list[tuple[str, str, int]], int, int]:
    """Logic."""
    dependencies = FileNotFoundSafeReqs(
        ExcludedReqs(
            FreezedReqs(requirements_file_content),
            excluded_reqs,
        ),
    ).reqs()
    packages = []
    sum_delta = 0
    max_delta = 0
    for name, version in track(dependencies, description='Scanning...'):
        delta = DaysDelta(
            version,
            CachedPackageList.ctor(
                SortedPackageList(
                    FilteredPackageList(
                        PypiPackageList(name),
                    ),
                ),
            ),
            datetime.datetime.now(tz=pytz.UTC).date(),
        ).days()
        sum_delta += delta
        max_delta = max(max_delta, delta)
        packages.append((name, version, delta))
    packages = sorted(packages, key=lambda row: row[2], reverse=True)
    return packages, sum_delta, max_delta


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
        Formats.default.value,
        '--format',
        help='Dependencies file format (default: "pip-freeze")',
    ),
) -> None:
    """Python project designed to calculate the lag or delay in dependencies in terms of days."""
    config = config_ctor(
        path_to_file,
        file_format,
        -1,
        -1,
    )
    console = Console()
    table = Table(show_header=True, header_style='bold magenta')
    table.add_column('Package')
    table.add_column('Version')
    table.add_column('Delta (days)')
    packages, sum_delta, max_delta = logic(
        config['path_to_file'].read_text(),
        config['excluded'],
    )
    for package, version, delta in packages:
        if delta != 0:
            table.add_row(package, version, str(delta))
    if len(packages) > 0:
        console.print(table)
        average_delta = '{0:.2f}'.format(sum_delta / len(packages))
    else:
        average_delta = '0'
    rich_print('Max delta: {0}'.format(max_delta))
    rich_print('Average delta: {0}'.format(average_delta))
    if config['fail_on_avg'] > -1 and float(average_delta) >= config['fail_on_avg']:
        rich_print('\n[red]Error: average delta greater than available[/red]')
        raise typer.Exit(code=1)
    if config['fail_on_max'] > -1 and max_delta >= config['fail_on_max']:
        rich_print('\n[red]Error: max delta greater than available[/red]')
        raise typer.Exit(code=1)
