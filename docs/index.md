# plaintest

A pytest plugin and CLI tool for managing plain-text test cases with Markdown documentation.

## Overview

`plaintest` helps you bridge the gap between human-readable test case documentation and automated tests. Write your test cases in simple Markdown files, link them to pytest tests using decorators, and generate HTML reports showing test coverage and results.

## Why plaintest?

Many teams struggle with test documentation scattered across multiple systems:

- Requirements in Jira
- Test cases in TestRail
- Implementation details in code comments
- Manual test scripts in spreadsheets

This fragmentation makes it hard to understand what's being tested and why.

**plaintest** solves this by keeping test cases as Markdown files in your repository alongside your code, maintaining a **single source of truth** that's:

- Version-controlled
- Code-review friendly
- Easily accessible to both humans and LLMs
- Integrated with your CI/CD pipeline

Changes to test specifications go through the same PR process as code changes, ensuring consistency and traceability.

## Key Features

- **Markdown Test Cases**: Write test cases in simple, readable Markdown
- **Pytest Integration**: Link test cases to pytest tests with a simple decorator
- **Coverage Reports**: See which test cases are covered by automated tests
- **HTML Reports**: Generate side-by-side reports showing test cases and their implementations
- **Tags & Metadata**: Organize test cases with frontmatter metadata
- **Media Support**: Include images and other media in your test cases
- **CLI Tool**: Manage test cases from the command line

## Quick Example

Create a test case:
```bash
plaintest add "User login functionality"
```

Link it to a pytest test:
```python
import pytest
from plaintest.markers import tc

@tc("001")
def test_user_login():
    # Your test implementation
    assert login(username="user", password="pass") == True
```

Generate a report:
```bash
plaintest coverage
```

## Installation

Install using pip:

```bash
pip install plaintest
```

Or with uv:

```bash
uv add plaintest
```

## Next Steps

- [Getting Started Guide](getting-started.md) - Set up your first project
- [Usage Examples](usage-examples.md) - Learn through practical examples
- [Configuration](configuration.md) - Customize plaintest for your project
- [API Reference](api-reference.md) - Explore all available features
