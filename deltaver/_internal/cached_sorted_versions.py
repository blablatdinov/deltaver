# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Cached sorted versions."""

import datetime
import json
from collections.abc import Sequence
from pathlib import Path
from typing import final

import attrs
from typing_extensions import override

from deltaver._internal.fk_package import FkPackage
from deltaver._internal.package import Package
from deltaver._internal.version_list import VersionList


@final
@attrs.define(frozen=True)
class CachedSortedVersions(VersionList):
    """Cached sorted versions."""

    _origin: VersionList
    _package_name: str

    @override
    def as_list(self) -> Sequence[Package]:  # noqa: WPS210. Simplify later
        """Sorted versions list."""
        cache_dir = Path('.deltaver_cache')
        (cache_dir / self._package_name).mkdir(exist_ok=True, parents=True)
        if cache_dir.exists():
            for cache_file in cache_dir.glob('**/*.json'):
                expected_filename = '{0}.json'.format(
                    datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d'),
                )
                if cache_file.name != expected_filename:
                    cache_file.unlink()
        cache_path = cache_dir / self._package_name / '{0}.json'.format(
            datetime.datetime.now(tz=datetime.timezone.utc).date(),
        )
        if cache_path.exists():
            res = []
            for package_info in json.loads(cache_path.read_text()):
                version_num = next(iter(package_info.keys()))
                release_date = datetime.datetime.strptime(
                    next(iter(package_info.values())),
                    '%Y-%m-%dT%H:%M:%S',
                ).astimezone(datetime.timezone.utc).date()
                res.append(FkPackage(self._package_name, version_num, release_date))
            return res
        origin_val = self._origin.as_list()
        cache_path.write_text(json.dumps([
            {str(package.version()): package.release_date().strftime('%Y-%m-%dT%H:%M:%S')}
            for package in origin_val
        ]))
        return origin_val
