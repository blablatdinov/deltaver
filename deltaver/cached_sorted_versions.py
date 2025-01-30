import datetime
import json
from pathlib import Path
from typing import final

import attrs
from typing_extensions import override

from deltaver.sorted_versions import SortedVersions
from deltaver.version_delta import SortedVersionsList


@final
@attrs.define(frozen=True)
class CachedSortedVersions(SortedVersions):
    """Cached sorted versions."""

    _origin: SortedVersions
    _package_name: str

    @override
    def fetch(self) -> SortedVersionsList:
        """Sorted versions list."""
        cache_dir = Path('.deltaver_cache')
        (cache_dir / self._package_name).mkdir(exist_ok=True, parents=True)
        if cache_dir.exists():
            for x in cache_dir.glob('**/*.json'):
                if x.name != '{0}.json'.format(datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%d')):
                    x.unlink()
        cache_path = cache_dir / self._package_name / '{0}.json'.format(
            datetime.datetime.now(tz=datetime.timezone.utc).date(),
        )
        if cache_path.exists():
            return [
                {
                    next(iter(elem.keys())): datetime.datetime.strptime(
                        next(iter(elem.values())),
                        '%Y-%m-%dT%H:%M:%S',
                    ).astimezone(datetime.timezone.utc).date(),
                }
                for elem  in json.loads(cache_path.read_text())
            ]
        origin_val = self._origin.fetch()
        cache_path.write_text(json.dumps([
            {next(iter(dict_.keys())): next(iter(dict_.values())).strftime('%Y-%m-%dT%H:%M:%S')}
            for dict_ in origin_val
        ]))
        return origin_val
