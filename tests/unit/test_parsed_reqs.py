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

"""Test parse pip requirements."""

from pathlib import Path

import pytest

from deltaver._internal.freezed_reqs import FreezedReqs
from deltaver._internal.golang_reqs import GolangReqs
from deltaver._internal.package_lock_reqs import PackageLockReqs
from deltaver._internal.poetry_lock_reqs import PoetryLockReqs


@pytest.mark.parametrize(
    ('text', 'expected'),
    [
        ('httpx==0.26.0', [('httpx', '0.26.0')]),
        ('txaio==22.2.1 ; python_version >= "3.9" and python_version < "3.10"', [('txaio', '22.2.1')]),
        ('twisted[tls]==22.8.0', [('twisted', '22.8.0')]),
        (
            '\n'.join([
                'zope-interface==5.4.0 ; python_version >= "3.9" and python_version < "3.10" \\',
                '    --hash=sha256:08f9636e99a9d5410181ba0729e0408d3d8748026ea938f3b970a0249daa8192 \\',
                '    --hash=sha256:0b465ae0962d49c68aa9733ba92a001b2a0933c317780435f00be7ecb959c702 \\',
                '    --hash=sha256:0cba8477e300d64a11a9789ed40ee8932b59f9ee05f85276dbb4b59acee5dd09',
            ]),
            [('zope-interface', '5.4.0')],
        ),
    ],
    ids=lambda line: line[0][0].split(' ')[0],
)
def test_correct(text: str, expected: str) -> None:
    """Test parsing pip requirements file."""
    got = FreezedReqs(text).reqs()

    assert got == expected


@pytest.mark.parametrize('text', [
    'deltaver @ file:///Users/almazilaletdinov/code/moment/deltaver',
    '-e git+https://github.com/blablatdinov/deltaver@77eb73d1ee66d4b2eed7fcb4ec889b8892b7ef2b#egg=deltaver',
])
def test_not_semvar(text: str) -> None:
    """Test not semver line."""
    got = FreezedReqs(text).reqs()

    assert got == []


def test_poetry_lock() -> None:
    """Test PoetryLockReqs."""
    got = PoetryLockReqs(
        Path('tests/fixtures/poetry_lock_example.lock').read_text(),
    ).reqs()

    assert got == [
        ('anyio', '4.2.0'),
        ('certifi', '2023.11.17'),
        ('colorama', '0.4.6'),
        ('h11', '0.14.0'),
        ('httpcore', '1.0.2'),
        ('httpx', '0.26.0'),
        ('idna', '3.6'),
        ('iniconfig', '2.0.0'),
        ('packaging', '23.2'),
        ('pluggy', '1.3.0'),
        ('pytest', '7.4.4'),
        ('sniffio', '1.3.0'),
    ]


def test_package_lock() -> None:
    """Test PackageLockReqs."""
    got = PackageLockReqs(
        Path('tests/fixtures/package-lock-example.json').read_text(),
    ).reqs()

    assert len(got) == 171
    assert got[0] == ('@sinonjs/commons', '1.8.2')
    assert [name for name, _ in got].count('camelcase-keys/camelcase') == 0
    assert got[-1] == ('yocto-queue', '0.1.0')
    assert got[143] == ('spdx-correct', '3.1.0')


def test_golang_reqs() -> None:
    """Test GolangReqs."""
    got = GolangReqs('\n'.join([
        'github.com/cpuguy83/go-md2man/v2 v2.0.5 h1:ZtcqGrnekaHpVLArFSe4HK5DoKx1T0rq2DwVB0alcyc=',
        'github.com/cpuguy83/go-md2man/v2 v2.0.5/go.mod h1:tgQtvFlXSQOSOSIRvRPT7W67SCa46tRHOmNcaadrF8o=',
        'github.com/russross/blackfriday/v2 v2.1.0 h1:JIOH55/0cWyOuilr9/qlrm0BSXldqnqwMsf35Ld67mk=',
        'github.com/russross/blackfriday/v2 v2.1.0/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=',
        'github.com/urfave/cli/v2 v2.27.5 h1:WoHEJLdsXr6dDWoJgMq/CboDmyY/8HMMH1fTECbih+w=',
        'github.com/urfave/cli/v2 v2.27.5/go.mod h1:3Sevf16NykTbInEnD0yKkjDAeZDS0A6bzhBH5hrMvTQ=',
        'github.com/xrash/smetrics v0.0.0-20240521201337-686a1a2994c1 h1:gEOO8jv9F4OT7lGCjxCBTO/36wtF6j2nSip77qHd4x4=',
        'github.com/xrash/smetrics v0.0.0-20240521201337-686a1a2994c1/go.mod h1:Ohn+xnUBiLI6FVj/9LpzZWtj1/D6lUovWYBkxHVV3aM=',  # noqa: E501
        'gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405 h1:yhCVgyC4o1eVCa2tZl7eS0r+SDo693bJlVdllGtEeKM=',
        'gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=',
        'gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=',
        'gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=',
    ])).reqs()

    assert got == [
        (
            'github.com/cpuguy83/go-md2man/v2',
            'v2.0.5',
        ),
        (
            'github.com/russross/blackfriday/v2',
            'v2.1.0',
        ),
        (
            'github.com/urfave/cli/v2',
            'v2.27.5',
        ),
        (
            'gopkg.in/yaml.v3',
            'v3.0.1',
        ),
    ]
