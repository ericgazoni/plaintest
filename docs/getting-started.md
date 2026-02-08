# Getting Started

This guide will walk you through setting up plaintest in your project and creating your first test case.

## Prerequisites

- Python 3.13 or higher
- pytest installed in your project

## Installation

Install plaintest using pip:

```bash
pip install plaintest
```

Or if you're using uv:

```bash
uv add plaintest
```

## Step 1: Initialize Your Project

Navigate to your project directory and initialize plaintest:

```bash
plaintest init
```

This creates a `test-cases` directory where all your test case Markdown files will be stored.

```
your-project/
├── test-cases/        # ← Created by plaintest init
├── tests/
└── pyproject.toml
```

## Step 2: Create Your First Test Case

Create a test case using the CLI:

```bash
plaintest add "User can login successfully"
```

This creates a structured Markdown file at `test-cases/001/case.md`:

```markdown
---
title: User can login successfully
tags: []
---

## Steps


## Expected

```

## Step 3: Write Your Test Case

Edit the generated Markdown file to document your test case:

```markdown
---
title: User can login successfully
tags: [authentication, critical]
---

## Steps

1. Navigate to the login page
2. Enter valid username: "testuser@example.com"
3. Enter valid password: "SecurePass123"
4. Click the "Login" button

## Expected

- User is redirected to the dashboard
- Welcome message displays the user's name
- Session is created and persists across page refreshes
```

## Step 4: Link to a Pytest Test

Create or update a pytest test to link it to your test case:

```python
# tests/test_auth.py
import pytest
from plaintest.markers import tc

@tc("001")
def test_user_login_success():
    """Test successful user login"""
    # Arrange
    client = TestClient()
    
    # Act
    response = client.login(
        username="testuser@example.com",
        password="SecurePass123"
    )
    
    # Assert
    assert response.status_code == 200
    assert response.redirected_to == "/dashboard"
    assert "Welcome" in response.text
```

!!! tip
    The `@tc("001")` decorator links this test to test case 001. You can link multiple tests to the same test case!

## Step 5: Run Your Tests

Run your pytest tests as usual:

```bash
pytest
```

## Step 6: Generate Coverage Report

See which test cases are covered by automated tests:

```bash
plaintest report
```

This displays a terminal report showing:

- Total test cases
- Cases with tests (covered)
- Cases without tests (uncovered)
- Coverage percentage

Example output:

```
Analyzing test coverage...

Total test cases: 5
Cases with tests: 4
Cases without tests: 1
Coverage: 80.0%

Cases without tests
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Test Case ID  ┃ Case File                  ┃ Title                      ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│      005      │ test-cases/005/case.md     │ Password reset flow        │
└───────────────┴────────────────────────────┴────────────────────────────┘
```

## Step 7: Generate HTML Report

Create a side-by-side HTML report showing test cases and their implementations:

```bash
plaintest html-report
```

This generates `.plaintest/plaintest-report.html` that you can open in your browser to see:

- Test cases with their full Markdown content
- Linked pytest test implementations with syntax highlighting
- Images and media embedded in test cases
- Tags and metadata

## Next Steps

Now that you have the basics, explore:

- [Usage Examples](usage-examples.md) - Learn advanced features and patterns
- [Configuration](configuration.md) - Customize plaintest for your needs
- [API Reference](api-reference.md) - Complete reference of all features

