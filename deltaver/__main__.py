from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Table
from typing_extensions import TypeAlias

from deltaver.config import CliOrPyprojectConfig, Config, ConfigDict, PyprojectTomlConfig
from deltaver.parsed_requirements import ExcludedReqs, FileNotFoundSafeReqs, FreezedReqs, PoetryLockReqs
from deltaver.version_delta import PypiVersionDelta, VersionsSortedBySemver

app = typer.Typer()
PackageName: TypeAlias = str
PackageVersion: TypeAlias = str
PackageDelta: TypeAlias = str


def results(
    packages: list[tuple[PackageName, PackageVersion, PackageDelta]],
    sum_delta: int,
    max_delta: int,
    config: Config,
) -> tuple[int, float]:
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
    if config.value_of('fail_on_avg') > -1 and float(average_delta) >= config.value_of('fail_on_avg'):
        print('\n[red]Error: average delta greater than available[/red]')
        raise typer.Exit(code=1)
    if config.value_of('fail_on_max') > -1 and max_delta >= config.value_of('fail_on_max'):
        print('\n[red]Error: max delta greater than available[/red]')
        raise typer.Exit(code=1)


@app.command()
def main(  # noqa: PLR0913
    path_to_requirements_file: str,
    file_format: Annotated[str, typer.Option('--format')] = 'freezed',
    fail_on_average: Annotated[int, typer.Option('--fail-on-avg')] = -1,
    fail_on_max: Annotated[int, typer.Option('--fail-on-max')] = -1,
    artifactory_domain: Annotated[str, typer.Option('--artifactory-domain')] = 'https://pypi.org',
    exclude_deps: Annotated[list[str], typer.Option('--exclude')] = [],  # noqa: B006
) -> None:
    res = 0
    max_delta = 0
    packages = []
    config = CliOrPyprojectConfig(
        PyprojectTomlConfig(Path('pyproject.toml')),
        ConfigDict({
            'file_format': file_format,
            'fail_on_avg': fail_on_average,
            'fail_on_max': fail_on_max,
            'artifactory_domain': artifactory_domain,
            'excluded': exclude_deps,
        }),
    )
    reqs_obj_ctor = {
        'freezed': FreezedReqs,
        'lock': PoetryLockReqs,
    }[config.value_of('file_format')]
    dependencies = FileNotFoundSafeReqs(
        ExcludedReqs(
            reqs_obj_ctor(Path(path_to_requirements_file)),
            config,
        ),
    ).reqs()
    for package, version in track(dependencies, description='Scanning...'):
        delta = PypiVersionDelta(
            VersionsSortedBySemver(
                config.value_of('artifactory_domain'),
                package,
            ),
            version,
        ).days()
        if delta > 0:
            packages.append(
                (package, version, str(delta)),
            )
        res += delta
        max_delta = max(max_delta, delta)
    packages = sorted(packages, key=lambda x: int(x[2]), reverse=True)
    results(packages, res, max_delta, config)


if __name__ == '__main__':
    app()
