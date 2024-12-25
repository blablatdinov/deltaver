<!-- 
The MIT License (MIT).

Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
-->
# Deltaver (Dependency Lag Calculator)

[![PyPI version](https://badge.fury.io/py/deltaver.svg)](https://badge.fury.io/py/deltaver)
![CI status](https://github.com/blablatdinov/deltaver/actions/workflows/pr-check.yml/badge.svg?branch=master)
[![Lines of code](https://tokei.rs/b1/github/blablatdinov/deltaver?type=python)](https://github.com/XAMPPRocky/tokei_rs)
[![Hits-of-Code](https://hitsofcode.com/github/blablatdinov/deltaver)](https://hitsofcode.com/github/blablatdinov/deltaver/view)

## Overview

The "Deltaver" is a Python project designed to calculate the lag or delay in dependencies in terms of days. It provides insights into how outdated your project dependencies are, helping you stay up-to-date with the latest developments and security patches.

## Features:

- **Dependency Lag Calculation**: The tool analyzes the timestamp of the current dependency version and compares it with the latest available version, providing the time lag in days.
- **Security Insights**: Identify outdated dependencies to prioritize updates based on security considerations.
- **Customization**: Configure the tool to focus on specific dependencies or categories, allowing for flexibility in analysis.

## Getting Started
### Prerequisites

Make sure you have the following installed:

- Python 3.x
- Pip (Python package installer)

### Installation

```bash
pip install deltaver
```

### Usage

Run deltaver:

```bash
deltaver requirements.txt
```

## License

This project is licensed under the MIT [License](LICENSE) - see the LICENSE file for details.
Acknowledgments
