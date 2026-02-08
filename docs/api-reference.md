# API Reference

Complete reference for all plaintest features and APIs.

## CLI Commands

### `plaintest init`

Initialize the test cases directory.

**Usage:**

```bash
plaintest init
```

**Description:**

Creates the test cases directory as configured in `pyproject.toml` (default: `test-cases/`).

**Options:** None

**Exit Codes:**

- `0` - Success

**Example:**

```bash
$ plaintest init
✓ Initialized test-cases
```

---

### `plaintest add`

Add new test case(s) interactively.

**Usage:**

```bash
plaintest add [TITLE]
```

**Arguments:**

- `TITLE` (optional) - The title of the test case to create

**Description:**

Creates a new test case with a unique ID in the next available numbered directory. If no title is provided, enters interactive mode where you can continuously add test cases. Press Ctrl+C when done.

**Options:** None

**Exit Codes:**

- `0` - Success

**Examples:**

```bash
# Interactive mode - continuously add test cases
$ plaintest add
Press Ctrl+C when done adding test cases

Enter test case title: User login
✓ Created test-cases/001/case.md

Enter test case title: User registration
✓ Created test-cases/002/case.md

Enter test case title: ^C
Done!

# With title argument - creates a single test case
$ plaintest add "User registration"
✓ Created test-cases/002/case.md

Done!
```

**Generated File Structure:**

```markdown
---
title: Your Title
tags: []
---

## Steps


## Expected

```

---

### `plaintest coverage`

Generate a terminal-based coverage report.

**Usage:**

```bash
plaintest coverage [OPTIONS]
```

**Options:**

- `--tests-dir PATH` - Directory containing test files (default: `tests`)

**Description:**

Analyzes test coverage by comparing test cases with pytest tests decorated with `@tc()`. Displays a summary table showing:

- Total test cases
- Cases with tests (covered)
- Cases without tests (uncovered)  
- Coverage percentage
- List of uncovered test cases
- Tests referencing non-existent test cases

**Exit Codes:**

- `N` - Where N is the number of uncovered test cases
- `0` - All test cases are covered

**Example Output:**

```bash
$ plaintest coverage
Analyzing test coverage...

Total test cases: 5
Cases with tests: 4
Cases without tests: 1
Coverage: 80.0%

Cases without tests
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Test Case ID  ┃ Case File               ┃ Title              ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│      005      │ test-cases/005/case.md  │ Password reset     │
└───────────────┴─────────────────────────┴────────────────────┘
```

---

### `plaintest report`

Generate an HTML report showing test cases alongside their pytest implementations.

**Usage:**

```bash
plaintest report [OPTIONS]
```

**Options:**

- `--tests-dir PATH` - Directory containing test files (default: `tests`)
- `--output PATH` - Output path for HTML report (default: `.plaintest/plaintest-report.html`)

**Description:**

Generates a side-by-side HTML report showing:

- Test case Markdown content with rendered formatting
- Embedded images and media
- Linked pytest test implementations with syntax highlighting
- Test case metadata (title, tags)
- Navigation between test cases

**Exit Codes:**

- `0` - Success
- `1` - Error (e.g., no test cases found)

**Examples:**

```bash
# Default output
$ plaintest report
Analyzing tests and generating report...
✓ HTML report generated: .plaintest/plaintest-report.html
Open the file in a browser to view the report

# Custom output location
$ plaintest report --output docs/coverage.html
✓ HTML report generated: docs/coverage.html

# Custom tests directory
$ plaintest report --tests-dir src/tests
```

## Python API

### Decorators

#### `tc(tc_id)`

Decorator to link a pytest test with a test case ID.

**Module:** `plaintest.markers`

**Parameters:**

- `tc_id` (str) - The test case ID (e.g., "001", "042")

**Returns:**

A decorator function that marks the test with the test case ID.

**Usage:**

```python
from plaintest.markers import tc

@tc("001")
def test_user_login():
    assert True

@tc("002")
def test_user_logout():
    assert True
```

**With Test Classes:**

```python
from plaintest.markers import tc
import pytest

class TestAuthentication:
    
    @tc("001")
    def test_login(self):
        assert True
    
    @tc("002")
    def test_logout(self):
        assert True
```

**Multiple Tests Per Case:**

```python
from plaintest.markers import tc

@tc("001")
def test_login_chrome():
    assert True

@tc("001")
def test_login_firefox():
    assert True
```

**Attributes:**

The decorator adds the following to the test function:

- `test_case_id` attribute containing the test case ID
- `pytest.mark.test_case(tc_id)` marker

---

### Configuration Functions

#### `get_test_cases_dir()`

Get the test cases directory from configuration.

**Module:** `plaintest.config`

**Returns:**

`Path` - The configured test cases directory path

**Example:**

```python
from plaintest.config import get_test_cases_dir

test_cases_dir = get_test_cases_dir()
print(f"Test cases directory: {test_cases_dir}")
# Output: Test cases directory: test-cases
```

---

#### `get_max_tc_id(test_cases_dir)`

Get the maximum test case ID from a directory.

**Module:** `plaintest.config`

**Parameters:**

- `test_cases_dir` (Path) - The test cases directory

**Returns:**

`int` - The maximum test case ID number, or 0 if no test cases exist

**Example:**

```python
from pathlib import Path
from plaintest.config import get_max_tc_id

test_dir = Path("test-cases")
max_id = get_max_tc_id(test_dir)
next_id = max_id + 1
print(f"Next test case ID: {next_id:0>3}")
# Output: Next test case ID: 043
```

---

### Analysis Functions

#### `find_undecorated_tests(test_cases_dir, tests_dir)`

Analyze test coverage by finding test cases without tests and tests without cases.

**Module:** `plaintest.analysis`

**Parameters:**

- `test_cases_dir` (Path) - Directory containing test cases
- `tests_dir` (Path) - Directory containing pytest tests

**Returns:**

`AnalysisResults` - Named tuple containing:

- `test_cases_without_tests` (set[str]) - Test case IDs without any tests
- `tests_without_test_cases` (set[str]) - Test case IDs referenced but don't exist
- `covered_test_cases` (set[str]) - Test case IDs with at least one test
- `decorated_tests` (dict[str, list[str]]) - Map of test case IDs to test node IDs

**Example:**

```python
from pathlib import Path
from plaintest.analysis import find_undecorated_tests

results = find_undecorated_tests(
    test_cases_dir=Path("test-cases"),
    tests_dir=Path("tests")
)

print(f"Covered: {len(results.covered_test_cases)}")
print(f"Uncovered: {len(results.test_cases_without_tests)}")
print(f"Invalid refs: {len(results.tests_without_test_cases)}")

for tc_id in results.test_cases_without_tests:
    print(f"  {tc_id}: No tests found")
```

---

#### `get_decorated_tests(tests_dir)`

Get all tests decorated with `@tc()` and their test case IDs.

**Module:** `plaintest.analysis`

**Parameters:**

- `tests_dir` (Path) - Directory containing pytest tests

**Returns:**

`dict[str, list[str]]` - Map of test case IDs to list of test node IDs

**Example:**

```python
from pathlib import Path
from plaintest.analysis import get_decorated_tests

decorated = get_decorated_tests(Path("tests"))

for tc_id, test_nodes in decorated.items():
    print(f"Test case {tc_id}:")
    for node in test_nodes:
        print(f"  - {node}")

# Output:
# Test case 001:
#   - tests/test_auth.py::test_login
#   - tests/test_auth.py::TestAuth::test_login_chrome
# Test case 002:
#   - tests/test_auth.py::test_logout
```

---

### Report Generation

#### `generate_html_report(test_cases_dir, decorated_tests, tests_dir, output_path)`

Generate an HTML report showing test cases and their implementations.

**Module:** `plaintest.html_report`

**Parameters:**

- `test_cases_dir` (Path) - Directory containing test cases
- `decorated_tests` (dict[str, list[str]]) - Map of test case IDs to test nodes
- `tests_dir` (Path) - Directory containing pytest tests  
- `output_path` (Path) - Output path for the HTML file

**Returns:**

None - Writes HTML file to `output_path`

**Example:**

```python
from pathlib import Path
from plaintest.analysis import get_decorated_tests
from plaintest.html_report import generate_html_report

test_cases_dir = Path("test-cases")
tests_dir = Path("tests")
output = Path("report.html")

decorated = get_decorated_tests(tests_dir)
generate_html_report(test_cases_dir, decorated, tests_dir, output)

print(f"Report generated: {output}")
```

---

## Data Structures

### Test Case File Format

Test cases are Markdown files with YAML frontmatter:

```markdown
---
title: string (required)
tags: array of strings (optional)
[custom_field]: any value (optional)
---

# Markdown content

Any Markdown content including:
- Headers
- Lists  
- Code blocks
- Images
- Tables
- etc.
```

**Required Fields:**

- `title` - Human-readable test case title

**Optional Fields:**

- `tags` - Array of string tags for categorization
- Custom fields - Any additional YAML fields for your needs

**Example:**

```markdown
---
title: User login with valid credentials
tags: [authentication, smoke, critical]
author: John Doe
requirement: REQ-AUTH-001
---

## Prerequisites

- User account exists in the system
- User knows valid credentials

## Steps

1. Navigate to /login
2. Enter email: user@example.com
3. Enter password: ValidPass123
4. Click "Login" button

## Expected

- User is redirected to /dashboard
- Welcome message displays user's name
- Session cookie is created

## Notes

This is a critical path test that should always pass.
```

---

### Test Node ID Format

Test node IDs follow pytest's node ID format:

```
path/to/file.py::test_function
path/to/file.py::TestClass::test_method
```

**Examples:**

```
tests/test_auth.py::test_login
tests/test_auth.py::TestAuth::test_login_success
tests/integration/test_api.py::TestUserAPI::test_get_user
```

---

### AnalysisResults

Named tuple returned by `find_undecorated_tests()`.

**Fields:**

- `test_cases_without_tests: set[str]` - Test case IDs without any linked tests
- `tests_without_test_cases: set[str]` - Test case IDs referenced in tests but don't exist
- `covered_test_cases: set[str]` - Test case IDs with at least one linked test
- `decorated_tests: dict[str, list[str]]` - Map of test case IDs to their test node IDs

**Example:**

```python
from plaintest.analysis import find_undecorated_tests
from pathlib import Path

results = find_undecorated_tests(
    Path("test-cases"),
    Path("tests")
)

# Access fields
print(results.test_cases_without_tests)  # {'005', '007'}
print(results.covered_test_cases)  # {'001', '002', '003', '004', '006'}
print(results.tests_without_test_cases)  # {'999'}
print(results.decorated_tests['001'])  # ['tests/test_auth.py::test_login']
```

---

## Pytest Plugin

The pytest plugin is automatically registered and provides:

### Markers

#### `test_case`

Marker added by the `@tc()` decorator.

**Usage:**

Automatically applied when using `@tc()` decorator. Can also be used directly:

```python
import pytest

@pytest.mark.test_case("001")
def test_something():
    assert True
```

However, prefer using `@tc()` for consistency:

```python
from plaintest.markers import tc

@tc("001")
def test_something():
    assert True
```

---

## Extending plaintest

### Custom Report Formats

You can create custom reports by using the analysis functions:

```python
from pathlib import Path
from plaintest.analysis import find_undecorated_tests
import json

# Analyze tests
results = find_undecorated_tests(
    Path("test-cases"),
    Path("tests")
)

# Create custom JSON report
report = {
    "total_cases": len(results.covered_test_cases) + len(results.test_cases_without_tests),
    "covered": len(results.covered_test_cases),
    "uncovered": len(results.test_cases_without_tests),
    "coverage_percent": len(results.covered_test_cases) / (len(results.covered_test_cases) + len(results.test_cases_without_tests)) * 100,
    "uncovered_cases": list(results.test_cases_without_tests),
    "invalid_references": list(results.tests_without_test_cases)
}

with open("coverage-report.json", "w") as f:
    json.dump(report, f, indent=2)
```

### Custom Test Case Templates

Override the default template:

```python
from string import Template
from pathlib import Path

CUSTOM_TEMPLATE = Template("""---
title: $title
tags: []
priority: medium
status: draft
---

## Description

Brief description of what this test case validates.

## Prerequisites

List any prerequisites or setup required.

## Steps

1. Step one
2. Step two
3. Step three

## Expected Result

Describe the expected outcome.

## Test Data

Any test data needed.

## Notes

Additional notes or references.
""")

# Use in your code
tc_file = Path("test-cases/001/case.md")
tc_file.write_text(CUSTOM_TEMPLATE.safe_substitute(title="My Test"))
```
