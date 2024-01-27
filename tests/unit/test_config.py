from pathlib import Path

import pytest

from deltaver.config import PyprojectTomlConfig


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    return Path('tests/fixtures/pyproject.toml')


def test(config_file: Path) -> None:
    config = PyprojectTomlConfig(config_file)

    assert config.value_of('fail_on_avg') == 6.5
    assert config.value_of('fail_on_max') == 10
