import datetime
from pathlib import Path
from typing import Annotated, Final

import toml
import typer
from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Table
from typing_extensions import TypeAlias

from deltaver.config import ConfigDict, Formats, Langs
from deltaver.parsed_requirements import (
    ExcludedReqs,
    FileNotFoundSafeReqs,
    FreezedReqs,
    PackageLockReqs,
    PoetryLockReqs,
)
from deltaver.version_delta import (
    CachedSortedVersions,
    DecrDelta,
    NpmjsVersionsSortedBySemver,
    OvertakingSafeVersionDelta,
    PypiVersionDelta,
    PypiVersionsSortedBySemver,
)

app = typer.Typer()
PackageName: TypeAlias = str
PackageVersion: TypeAlias = str
PackageDelta: TypeAlias = float
FIRST_DATE: Final = datetime.datetime(
    1, 1, 1, tzinfo=datetime.timezone.utc,
).date()
FIRST_DATE_STR: Final = '0001-01-01'


def results(
    packages: list[tuple[PackageName, PackageVersion, PackageDelta]],
    sum_delta: int,
    max_delta: int,
    config: ConfigDict,
) -> None:
    console = Console()
    table = Table(show_header=True, header_style='bold magenta')
    table.add_column('Package')
    table.add_column('Version')
    table.add_column('Delta (days)')
    for package, version, delta in packages:
        if delta != 0:
            table.add_row(package, version, str(delta))
    if len(packages) > 0:
        console.print(table)
        average_delta = '{0:.2f}'.format(sum_delta / len(packages))
    else:
        average_delta = '0'
    print('Max delta: {0}'.format(max_delta))
    print('Average delta: {0}'.format(average_delta))
    if config['fail_on_avg'] > -1 and float(average_delta) >= config['fail_on_avg']:
        print('\n[red]Error: average delta greater than available[/red]')
        raise typer.Exit(code=1)
    if config['fail_on_max'] > -1 and max_delta >= config['fail_on_max']:
        print('\n[red]Error: max delta greater than available[/red]')
        raise typer.Exit(code=1)


def controller(
    config: ConfigDict,
) -> tuple[
    list[tuple[PackageName, PackageVersion, PackageDelta]],
    int,
    int,
    ConfigDict,
]:
    sum_delta = 0
    max_delta = 0
    packages = []
    lang_format = {
        'js': {
            'lock': (PackageLockReqs, NpmjsVersionsSortedBySemver),
        },
        'py': {
            'freezed': (FreezedReqs, PypiVersionsSortedBySemver),
            'lock': (PoetryLockReqs, PypiVersionsSortedBySemver),
        },
    }[config['lang'].value]
    reqs_obj_ctor, sorted_versions_ctor = lang_format[config['file_format'].value]  # type: ignore [index]
    dependencies = FileNotFoundSafeReqs(
        ExcludedReqs(
            reqs_obj_ctor(config['path_to_requirements_file']),
            config,
        ),
    ).reqs()
    for package, version in track(dependencies, description='Scanning...'):
        delta = OvertakingSafeVersionDelta(
            DecrDelta(
                PypiVersionDelta(
                    CachedSortedVersions(
                        sorted_versions_ctor(
                            config['artifactory_domain'],
                            package,
                        ),
                        package,
                    ),
                    version,
                ),
                config['for_date'],
            ),
            config['for_date'] == FIRST_DATE,
        ).days()
        packages.append(
            (package, version, delta),
        )
        sum_delta += delta
        max_delta = max(max_delta, delta)
    return (
        sorted(packages, key=lambda x: int(x[2]), reverse=True),
        sum_delta,
        max_delta,
        config,
    )


@app.command()
def main(  # noqa: PLR0913
    path_to_requirements_file: str,
    file_format: Annotated[str, typer.Option('--format')] = 'freezed',
    fail_on_average: Annotated[int, typer.Option('--fail-on-avg')] = -1,
    fail_on_max: Annotated[int, typer.Option('--fail-on-max')] = -1,
    artifactory_domain: Annotated[str, typer.Option('--artifactory-domain')] = 'https://pypi.org',
    exclude_deps: Annotated[list[str], typer.Option('--exclude')] = [],  # noqa: B006
    # Use unreal date because time_machine.move_to fixture not work for datetime.datetime.now() here
    for_date_param: Annotated[datetime.datetime, typer.Option('--for-date')] = FIRST_DATE_STR,  # type: ignore[assignment]
    lang: Annotated[str, typer.Option('--lang')] = 'py',
) -> None:
    if for_date_param.date() == FIRST_DATE:
        for_date = datetime.datetime.now(tz=datetime.timezone.utc)
    else:
        for_date = for_date_param
    pyproject_config_path = Path('pyproject.toml')
    if not pyproject_config_path.exists():
        pyproject_config = {}
    else:
        pyproject_config = toml.loads(pyproject_config_path.read_text()).get('tool', {}).get('deltaver', {})
    config = ConfigDict({
        'path_to_requirements_file': (
            pyproject_config.get('path_to_requirements_file')
            or Path(path_to_requirements_file)
        ),
        'lang': Langs(lang),
        'file_format': Formats(file_format),
        'fail_on_avg': pyproject_config.get('fail_on_avg') or fail_on_average,
        'fail_on_max': pyproject_config.get('fail_on_max') or fail_on_max,
        'artifactory_domain': pyproject_config.get(
            'artifactory_domain',
            {'js': 'https://registry.npmjs.org', 'py': 'https://pypi.org'}.get(lang),
        ) or artifactory_domain,
        'excluded': pyproject_config.get('excluded') or exclude_deps,
        'for_date': pyproject_config.get('for_date') or for_date.date(),
    })
    results(*controller(config))


if __name__ == '__main__':
    app()
