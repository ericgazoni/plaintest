# plaintest

A pytest plugin and CLI tool for managing plain-text test cases with Markdown documentation.

## Overview

`plaintest` helps you bridge the gap between human-readable test case documentation and automated tests. 
Write your test cases in simple Markdown files, link them to pytest tests using decorators, 
and generate HTML reports showing test coverage and results.

## Rationale
Many teams struggle with test documentation scattered across multiple systems: 
requirements in Jira, test cases in TestRail, implementation details in code comments. 
This fragmentation makes it hard to understand what's being tested and why. 
By keeping test cases as Markdown files in your repository alongside your code, 
you maintain a single source of truth that's version-controlled, code-review friendly, 
and easily accessible to both humans and LLMs. 

Changes to test specifications go through the same PR process as code changes, ensuring consistency and traceability.

## Installation

```bash
pip install plaintest
```

Or with uv:
```bash
uv add plaintest
```

## Quick Start

1. **Initialize your test cases directory**:
```bash
plaintest init
```

2. **Create a test case**:
```bash
plaintest add "User login functionality"
```

This creates a Markdown file like `test-cases/001/case.md`:
```markdown
---
title: User login functionality
tags: []
---

## Steps


## Expected

```

   *Tip: Create a `.template` file in your test cases directory to customize the template using Jinja2 syntax.*

3. **Link a pytest test to the test case**:
```python
import pytest

@pytest.mark.tc("001")
def test_user_login():
    # Your test implementation
    assert True
```

4. **Generate a coverage report**:
```bash
plaintest report
```

## Configuration

Add configuration to your `pyproject.toml`:

```toml
[tool.plaintest]
test_cases_dir = "test-cases"
```

## Commands

- `plaintest init` - Initialize test cases directory
- `plaintest add [TITLE]` - Interactively add new test case(s)
- `plaintest report` - Generate terminal-based coverage report
- `plaintest html-report` - Generate side-by-side HTML report

## License

MIT

