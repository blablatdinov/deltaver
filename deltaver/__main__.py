import enum
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Table
from typing_extensions import TypeAlias

from deltaver.parsed_requirements import FreezedReqs, PoetryLockReqs
from deltaver.version_delta import PypiVersionDelta, VersionsSortedBySemver

app = typer.Typer()
PackageName: TypeAlias = str
PackageVersion: TypeAlias = str
PackageDelta: TypeAlias = str


class Formats(enum.Enum):

    freezed = 'freezed'
    lock = 'lock'


def format_output(
    packages: list[tuple[PackageName, PackageVersion, PackageDelta]],
    sum_delta: int,
    max_delta: int,
) -> None:
    console = Console()
    table = Table(show_header=True, header_style='bold magenta')
    table.add_column('Package')
    table.add_column('Version')
    table.add_column('Delta (days)')
    for package, version, delta in packages:
        table.add_row(package, version, delta)
    if len(packages) > 0:
        console.print(table)
        average_delta = '{0:.2f}'.format(sum_delta / len(packages))
    else:
        average_delta = '0'
    print('Max delta: {0}'.format(max_delta))
    print('Average delta: {0}'.format(average_delta))


@app.command()
def main(
    path_to_requirements_file: str,
    file_format: Annotated[str, typer.Option('--format')] = 'freezed',
) -> None:
    res = 0
    max_delta = 0
    packages = []
    reqs_obj_ctor = {
        'freezed': FreezedReqs,
        'lock': PoetryLockReqs,
    }[file_format]
    for package, version in track(reqs_obj_ctor(Path(path_to_requirements_file)).reqs(), description='Scanning...'):
        delta = PypiVersionDelta(VersionsSortedBySemver(package), version).days()
        if delta > 0:
            packages.append(
                (package, version, str(delta)),
            )
        res += delta
        max_delta = max(max_delta, delta)
    packages = sorted(packages, key=lambda x: int(x[2]), reverse=True)
    format_output(packages, res, max_delta)


if __name__ == '__main__':
    app()
