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

"""Test mix.lock requirements file."""


from deltaver.mix_lock_reqs import MixLockReqs


def test_mix_lock_reqs() -> None:
    """Test mix.lock requirements parsing."""
    mix_file = '\n'.join([
        '%{'
        '  "phoenix": {:hex, :phoenix, "1.8.0", "dc5d256bb253110266ded8c4a6a167e24fabde2e14b8e474d262840ae8d8ea18", [:mix], [{:bandit, "~> 1.0", [hex: :bandit, repo: "hexpm", optional: true]}, {:jason, "~> 1.0", [hex: :jason, repo: "hexpm", optional: true]}, {:phoenix_pubsub, "~> 2.1", [hex: :phoenix_pubsub, repo: "hexpm", optional: false]}, {:phoenix_template, "~> 1.0", [hex: :phoenix_template, repo: "hexpm", optional: false]}, {:phoenix_view, "~> 2.0", [hex: :phoenix_view, repo: "hexpm", optional: true]}, {:plug, "~> 1.14", [hex: :plug, repo: "hexpm", optional: false]}, {:plug_cowboy, "~> 2.7", [hex: :plug_cowboy, repo: "hexpm", optional: true]}, {:plug_crypto, "~> 1.2 or ~> 2.0", [hex: :plug_crypto, repo: "hexpm", optional: false]}, {:telemetry, "~> 0.4 or ~> 1.0", [hex: :telemetry, repo: "hexpm", optional: false]}, {:websock_adapter, "~> 0.5.3", [hex: :websock_adapter, repo: "hexpm", optional: false]}], "hexpm", "15f6e9cb76646ad8d9f2947240519666fc2c4f29f8a93ad9c7664916ab4c167b"},',  # noqa: E501
        '  "ecto": {:hex, :ecto, "3.13.2", "7d0c0863f3fc8d71d17fc3ad3b9424beae13f02712ad84191a826c7169484f01", [:mix], [{:decimal, "~> 2.0", [hex: :decimal, repo: "hexpm", optional: false]}, {:jason, "~> 1.0", [hex: :jason, repo: "hexpm", optional: true]}, {:telemetry, "~> 0.4 or ~> 1.0", [hex: :telemetry, repo: "hexpm", optional: false]}], "hexpm", "669d9291370513ff56e7b7e7081b7af3283d02e046cf3d403053c557894a0b3e"},',  # noqa: E501
        '}',
    ])

    assert MixLockReqs(mix_file).reqs() == [
        ('phoenix', '1.8.0'),
        ('ecto', '3.13.2'),
    ]


def test_mix_lock_reqs_empty() -> None:
    """Test mix.lock requirements parsing with empty content."""
    assert MixLockReqs('%{}').reqs() == []


def test_mix_lock_reqs_with_git_deps() -> None:
    """Test mix.lock requirements parsing with git dependencies."""
    mix_file = '\n'.join([
        '%{',
        '  "phoenix": {:hex, :phoenix, "1.8.0", "dc5d256bb253110266ded8c4a6a167e24fabde2e14b8e474d262840ae8d8ea18", [:mix], [], "hexpm", "15f6e9cb76646ad8d9f2947240519666fc2c4f29f8a93ad9c7664916ab4c167b"},',  # noqa: E501
        '  "heroicons": {:git, "https://github.com/tailwindlabs/heroicons.git", "0435d4ca364a608cc75e2f8683d374e55abbae26", [tag: "v2.2.0", sparse: "optimized", depth: 1]},',  # noqa: E501
        '}',
    ])

    assert MixLockReqs(mix_file).reqs() == [
        ('phoenix', '1.8.0'),
    ]
