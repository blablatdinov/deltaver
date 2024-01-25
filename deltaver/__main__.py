from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.progress import track
from rich.table import Table

from deltaver.version_delta import PypiVersionDelta

app = typer.Typer()


@app.command()
def main(path_to_requirements_file: str):
    x = []
    res = 0
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Package")
    table.add_column("Version")
    table.add_column("Delta (days)")
    lines = Path(path_to_requirements_file).read_text().strip().splitlines()
    packages = []
    for line in track(lines, description='Scanning...'):
        package, version = line.split('==')
        delta = PypiVersionDelta(package, version).days()
        if delta > 0:
            packages.append(
                (package, version, str(delta)),
            )
        res += delta
    packages = sorted(packages, key=lambda x: int(x[2]), reverse=True)
    for package, version, delta in packages:
        table.add_row(package, version, delta)
    console.print(table)
    print('Average delta: {0:.3}'.format(res / len(lines)))


if __name__ == '__main__':
    app()
