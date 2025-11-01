# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Test GolangReqs."""

from deltaver._internal.golang_reqs import GolangReqs


def test_version_number() -> None:
    """Test version number."""
    got = GolangReqs('\n'.join([
        'filippo.io/edwards25519 v1.1.0 h1:FNf4tywRC1HmFuKW5xopWpigGjJKiJSV0Cqo0cJWDaA=',
        'filippo.io/edwards25519 v1.1.0/go.mod h1:BxyFTGdWcka3PhytdK4V28tE5sGfRvvvRV7EaN4VDT4=',
    ])).reqs()

    assert got == [('filippo.io/edwards25519', 'v1.1.0')]


def test_last_version() -> None:
    """Test last version."""
    got = GolangReqs('\n'.join([
        'github.com/aws/aws-sdk-go-v2 v1.38.1 h1:j7sc33amE74Rz0M/PoCpsZQ6OunLqys/m5antM0J+Z8=',
        'github.com/aws/aws-sdk-go-v2 v1.38.1/go.mod h1:9Q0OoGQoboYIAJyslFyF1f5K1Ryddop8gqMhWx/n4Wg=',
        'github.com/aws/aws-sdk-go-v2 v1.38.0 h1:UCRQ5mlqcFk9HJDIqENSLR3wiG1VTWlyUfLDEvY7RxU=',
        'github.com/aws/aws-sdk-go-v2 v1.38.0/go.mod h1:9Q0OoGQoboYIAJyslFyF1f5K1Ryddop8gqMhWx/n4Wg=',
    ])).reqs()

    assert got == [('github.com/aws/aws-sdk-go-v2', 'v1.38.1')]
