from pathlib import Path
from shutil import copyfile

import pytest

from deltaver.config import PyprojectTomlConfig


@pytest.fixture()
def config_file(tmp_path):
    # path = tmp_path / 'pyproject.toml'
    # shutil(Path('tests/fixtures/pyproject.toml'), path)
    # return path
    return Path('tests/fixtures/pyproject.toml')


def test(config_file):
    config = PyprojectTomlConfig(config_file) 

    assert config.value_of('fail_on_avg') == 6.5
    assert config.value_of('fail_on_max') == 10
