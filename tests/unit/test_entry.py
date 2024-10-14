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

import datetime
import zipfile
from pathlib import Path

import httpx
import pytest
import respx
from time_machine import TimeMachineFixture

from deltaver.entry import logic


@pytest.fixture()
def _mock_pypi(respx_mock: respx.router.MockRouter, tmp_path: Path) -> None:
    with zipfile.ZipFile("tests/fixtures/pypi_mock.zip", "r") as zip_ref:
        zip_ref.extractall(tmp_path)
    for line in Path("tests/fixtures/requirements.txt").read_text().strip().splitlines():
        package_name = line.split("==")[0]
        respx_mock.get("https://pypi.org/pypi/{0}/json".format(package_name)).mock(
            return_value=httpx.Response(
                200,
                text=Path(tmp_path / "fixtures/{0}_pypi_response.json".format(package_name)).read_text(),
            )
        )


@pytest.mark.usefixtures("_mock_pypi")
def test(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    packages, sum_delta, max_delta = logic(Path("tests/fixtures/requirements.txt").read_text(), [])

    assert [(name, version, delta) for name, version, delta in packages if delta > 0] == [
        ("SQLAlchemy", "1.4.51", 366),
        ("smmap", "5.0.1", 132),
        ("jsonschema", "4.21.0", 8),
        ("MarkupSafe", "2.1.3", 8),
        ("diff_cover", "8.0.2", 7),
        ("bandit", "1.7.6", 4),
        ("cryptography", "41.0.7", 4),
        ("pluggy", "1.3.0", 3),
        ("refurb", "1.27.0", 3),
    ]
    assert sum_delta == 535
    assert max_delta == 366


@pytest.mark.usefixtures('_mock_pypi')
@respx.mock(assert_all_mocked=False)
def test_excluded(time_machine: TimeMachineFixture) -> None:
    time_machine.move_to(datetime.datetime(2024, 1, 27, tzinfo=datetime.timezone.utc))
    packages, sum_delta, max_delta = logic(
        Path("tests/fixtures/requirements.txt").read_text(),
        ['sqlalchemy', 'bandit'],
    )

    assert [(name, version, delta) for name, version, delta in packages if delta > 0] == [
        ("smmap", "5.0.1", 132),
        ("jsonschema", "4.21.0", 8),
        ("MarkupSafe", "2.1.3", 8),
        ("diff_cover", "8.0.2", 7),
        ("cryptography", "41.0.7", 4),
        ("pluggy", "1.3.0", 3),
        ("refurb", "1.27.0", 3),
    ]
    assert sum_delta == 165
    assert max_delta == 132
