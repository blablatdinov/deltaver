# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Integration test for mix.lock functionality."""

from pathlib import Path

import pytest

from deltaver.entry import logic
from deltaver._internal.formats import Formats


@pytest.mark.slow
def test_mix_lock_integration() -> None:
    """Test integration with mix.lock file."""
    packages, sum_delta, max_delta = logic(
        Path('tests/fixtures/mix-example.lock').read_text(),
        [],  # excluded packages
        Formats.mix_lock,
    )
    assert len(packages) > 0
    assert sum_delta >= 0
    assert max_delta >= 0
