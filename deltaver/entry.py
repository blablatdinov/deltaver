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

import toml
import datetime
import sys
import traceback
from pathlib import Path
from typing import Annotated

import pytz
import typer
from rich import print as rich_print
from rich.console import Console
from rich.progress import track
from rich.table import Table

from deltaver.cached_package_list import CachedPackageList
from deltaver.config import Config, UnfillableConfig
from deltaver.delta import DaysDelta
from deltaver.filtered_package_list import FilteredPackageList
from deltaver.formats import Formats
from deltaver.npmjs_package_list import NpmjsPackageList
from deltaver.parsed_requirements import ExcludedReqs, FileNotFoundSafeReqs, FreezedReqs, PackageLockReqs, ParsedReqs
from deltaver.pypi_package_list import PypiPackageList
from deltaver.sorted_package_list import SortedPackageList
from deltaver.version_list import VersionList

app = typer.Typer()


def config_from_cli(
    path_to_file: Path,
    file_format: Formats,
    fail_on_avg: int,
    fail_on_max: int,
) -> UnfillableConfig:
    return UnfillableConfig({
        'path_to_file': path_to_file,
        'file_format': file_format,
        'excluded': [],  # TODO
        'fail_on_avg': None if fail_on_avg == -1 else fail_on_avg,
        'fail_on_max': None if fail_on_max == -1 else fail_on_max,
    })


def pyproject_config() -> UnfillableConfig:
    try:
        pyproject_config_path = Path('pyproject.toml')
        pyproject_config = toml.loads(pyproject_config_path.read_text()).get('tool', {}).get('deltaver', {})
    except FileNotFoundError:
        pyproject_config = {}
    return Config({
        'path_to_file': pyproject_config.get('path_to_file'),
        'file_format': pyproject_config.get('path_to_file'),
        'excluded': pyproject_config.get('path_to_file', []),  # TODO
        'fail_on_avg': pyproject_config.get('path_to_file'),
        'fail_on_max': pyproject_config.get('path_to_file'),
    })


def config_ctor(
    cli_config: Config,
    pyproject_config: Config,
) -> Config:
    """Ctor for config."""
    config = Config({
        'path_to_file': pyproject_config.get('path_to_file', cli_config['path_to_file']),
        'file_format': pyproject_config.get('file_format', cli_config['file_format']),
        'excluded': pyproject_config.get('excluded', []),  # TODO
        'fail_on_avg': pyproject_config.get('fail_on_avg', cli_config['fail_on_avg']),
        'fail_on_max': pyproject_config.get('fail_on_max', cli_config['fail_on_max']),
    })
    if config['file_format'] == Formats.default:
        config['file_format'] = Formats.pip_freeze
    return config


def logic(  # noqa: WPS210, WPS234. TODO: fix
    requirements_file_content: str,
    excluded_reqs: list[str],
    file_format: Formats,
) -> tuple[list[tuple[str, str, int]], int, int]:
    """Logic."""
    file_format = Formats.pip_freeze if file_format == Formats.default else file_format
    parsed_reqs: ParsedReqs = {
        Formats.npm_lock: PackageLockReqs(requirements_file_content),
        Formats.pip_freeze: FreezedReqs(requirements_file_content),
    }[file_format]
    dependencies = FileNotFoundSafeReqs(
        ExcludedReqs(
            parsed_reqs,
            excluded_reqs,
        ),
    ).reqs()
    packages = []
    sum_delta = 0
    max_delta = 0
    for name, version in track(dependencies, description='Scanning...'):
        package_list: VersionList = {
            Formats.npm_lock: NpmjsPackageList(name),
            Formats.pip_freeze: PypiPackageList(name),
        }[file_format]
        delta = DaysDelta(
            version,
            CachedPackageList.ctor(
                SortedPackageList(
                    FilteredPackageList(
                        package_list,
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


def cli(  # noqa: WPS210, WPS213. TODO: fix
    path_to_file: Path,
    file_format: Formats,
    fail_on_average: int,
    fail_on_max: int,
) -> None:
    """Cli."""
    config = config_ctor(
        config_from_cli(
            path_to_file,
            file_format,
            fail_on_average,
            fail_on_max,
        ),
        pyproject_config(),
    )
    console = Console()
    table = Table(show_header=True, header_style='bold magenta')
    table.add_column('Package')
    table.add_column('Version')
    table.add_column('Delta (days)')
    packages, sum_delta, max_delta = logic(
        config['path_to_file'].read_text(),
        config['excluded'],
        file_format,
    )
    for package, version, delta in packages:
        if delta != 0:
            table.add_row(package, version, str(delta))
    if packages:
        console.print(table)
        average_delta = '{0:.2f}'.format(sum_delta / len(packages))
    else:
        average_delta = '0'
    rich_print('Max delta: {0}'.format(max_delta))
    rich_print('Average delta: {0}'.format(average_delta))
    if config['fail_on_avg'] > -1 and float(average_delta) >= config['fail_on_avg']:  # noqa: WPS221, WPS333. TODO: fix
        rich_print('\n[red]Error: average delta greater than available[/red]')
        raise typer.Exit(code=1)
    if config['fail_on_max'] > -1 and max_delta >= config['fail_on_max']:  # noqa: WPS333. TODO: fix
        rich_print('\n[red]Error: max delta greater than available[/red]')
        raise typer.Exit(code=1)


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
    fail_on_average: Annotated[int, typer.Option('--fail-on-avg')] = -1,
    fail_on_max: Annotated[int, typer.Option('--fail-on-max')] = -1,
) -> None:
    """Python project designed to calculate the lag or delay in dependencies in terms of days."""
    try:
        cli(path_to_file, file_format, fail_on_average, fail_on_max)
    except Exception as err:  # noqa: BLE001. Application entrypoint
        sys.stdout.write('\n'.join([
            'Deltaver fail with: "{0}"'.format(err),
            'Please submit it to https://github.com/blablatdinov/deltaver/issues',
            'Copy and paste this stack trace to GitHub:',
            '========================================',
            traceback.format_exc(),
        ]))
        sys.exit(1)
