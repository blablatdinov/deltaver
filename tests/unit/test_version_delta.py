from deltaver.version_delta import PypiVersionDelta


def test():
    assert PypiVersionDelta('', '').days() == 1
