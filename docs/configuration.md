# Configuration

Learn how to customize plaintest for your project.

## Configuration File

plaintest is configured through your `pyproject.toml` file. All configuration goes under the `[tool.plaintest]` section.

### Basic Configuration

```toml
[tool.plaintest]
test_cases_dir = "test-cases"
```

## Configuration Options

### `test_cases_dir`

**Type:** `string`  
**Default:** `"test-cases"`

The directory where test case Markdown files are stored.

```toml
[tool.plaintest]
test_cases_dir = "test-cases"
```

You can use a different directory name if desired:

```toml
[tool.plaintest]
test_cases_dir = "specs"
```

Or organize by subdirectories:

```toml
[tool.plaintest]
test_cases_dir = "docs/test-cases"
```

## Directory Structure

plaintest expects test cases to be organized in numbered directories:

```
test-cases/
├── 001/
│   ├── case.md
│   └── screenshot.png
├── 002/
│   └── case.md
├── 003/
│   ├── case.md
│   ├── diagram.svg
│   └── expected-output.json
└── ...
```

Each directory contains:

- `case.md` - The test case Markdown file (required)
- Any media files referenced in the test case (optional)

## Test Case Format

### Frontmatter

Test cases use YAML frontmatter for metadata:

```markdown
---
title: Test case title
tags: [tag1, tag2, tag3]
---

## Content goes here
```

#### Required Fields

- **`title`**: The human-readable title of the test case

#### Optional Fields

- **`tags`**: Array of tags for categorization

### Sections

While plaintest doesn't enforce a specific structure, we recommend these sections:

```markdown
---
title: Your test case title
tags: [category, priority]
---

## Prerequisites

Any setup or preconditions needed

## Steps

1. Step one
2. Step two
3. Step three

## Expected

Expected results or outcomes

## Notes

Any additional information
```

## Pytest Configuration

### Registering the Plugin

The plaintest pytest plugin is automatically registered via the entry point in `pyproject.toml`:

```toml
[project.entry-points.pytest11]
plaintest = "plaintest.plugin"
```

### Using the Marker

Import and use the `tc` decorator in your tests:

```python
from plaintest.markers import tc

@tc("001")
def test_something():
    assert True
```

The `@tc()` decorator accepts a string test case ID.

### Pytest Markers

plaintest automatically registers a `test_case` marker. You can configure it in `pytest.ini` or `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "test_case: marks tests as linked to a test case ID"
]
```

## Command-Line Options

### `plaintest init`

Initialize the test cases directory.

```bash
plaintest init
```

Creates the configured `test_cases_dir` if it doesn't exist.

### `plaintest add`

Add new test case(s) interactively.

**Usage:**

```bash
# Interactive mode
plaintest add

# With title argument
plaintest add "Test case title"
```

**Options:** None

### `plaintest report`

Generate a terminal-based coverage report.

**Usage:**

```bash
plaintest report [OPTIONS]
```

**Options:**

- `--tests-dir PATH` - Directory containing test files (default: `tests`)

**Examples:**

```bash
# Use default tests directory
plaintest report

# Specify tests directory
plaintest report --tests-dir src/tests
```

**Exit Codes:**

The command exits with the number of uncovered test cases:

- `0` - All test cases are covered
- `N` - N test cases are not covered

This is useful for CI/CD pipelines to fail builds on low coverage.

### `plaintest html-report`

Generate an HTML report showing test cases alongside their implementations.

**Usage:**

```bash
plaintest html-report [OPTIONS]
```

**Options:**

- `--tests-dir PATH` - Directory containing test files (default: `tests`)
- `--output PATH` - Output path for the HTML report (default: `.plaintest/plaintest-report.html`)

**Examples:**

```bash
# Use defaults
plaintest html-report

# Custom output location
plaintest html-report --output reports/test-cases.html

# Custom tests directory
plaintest html-report --tests-dir src/tests

# Both options
plaintest html-report --tests-dir src/tests --output docs/coverage.html
```

## Multiple Projects Configuration

If you have multiple projects or test suites, you can maintain separate test case directories:

### Monorepo Setup

```toml
# Root pyproject.toml
[tool.plaintest]
test_cases_dir = "test-cases/integration"
```

Then use command-line options to work with different test suites:

```bash
# Integration tests
plaintest report --tests-dir tests/integration

# Unit tests (with separate test cases)
plaintest report --tests-dir tests/unit
```

### Multiple Configuration Files

For complex setups, consider separate configuration files:

```
project/
├── pyproject.toml              # Main config
├── integration/
│   ├── pyproject.toml          # Integration test config
│   ├── test-cases/
│   └── tests/
└── e2e/
    ├── pyproject.toml          # E2E test config
    ├── test-cases/
    └── tests/
```

## Environment Variables

Currently, plaintest does not use environment variables for configuration. All configuration is done through `pyproject.toml`.

## Best Practices

### 1. Keep Test Cases in Version Control

Always commit your test cases directory:

```bash
git add test-cases/
git commit -m "Add test cases for new feature"
```

### 2. Use Consistent Naming

Stick to the numbered directory format:

✅ Good:
```
test-cases/001/
test-cases/002/
test-cases/010/
```

❌ Bad:
```
test-cases/tc-001/
test-cases/case_02/
test-cases/test10/
```

### 3. Document Your Tagging Strategy

Create a convention for tags and document it in your project:

```markdown
# Test Case Tags

- **smoke**: Critical path tests
- **regression**: Full regression suite
- **integration**: Integration tests
- **unit**: Unit tests
- **critical**: High-priority tests
- **feature-xyz**: Feature-specific tests
```

### 4. Review Test Cases in PRs

Include test case changes in code reviews:

```bash
git diff test-cases/
```

This ensures test documentation stays accurate and up-to-date.

### 5. Archive Obsolete Test Cases

Instead of deleting old test cases, consider archiving them:

```
test-cases/
├── 001/
├── 002/
└── archived/
    ├── old-001/
    └── old-002/
```

Or add an `archived: true` field in the frontmatter:

```yaml
---
title: Obsolete feature test
archived: true
tags: [archived]
---
```

### 6. Link Test Cases to Requirements

Use the frontmatter to link test cases to requirements:

```yaml
---
title: User login test
tags: [authentication]
requirement: REQ-AUTH-001
jira: PROJ-1234
---
```

This creates traceability between requirements and tests.

## Troubleshooting

### Test cases not found

**Problem:** `plaintest report` shows no test cases.

**Solution:** Check your `test_cases_dir` configuration matches the actual directory name.

### Tests not linked to test cases

**Problem:** Tests appear in "Tests without test cases" section.

**Solution:** 

1. Verify the test case ID exists in the test cases directory
2. Check that the ID in `@tc("001")` matches the directory name
3. Ensure the directory name is zero-padded (e.g., `001` not `1`)

### HTML report not generated

**Problem:** `plaintest html-report` fails or produces empty report.

**Solution:**

1. Ensure at least one test has the `@tc()` decorator
2. Check that the output directory is writable
3. Verify test case Markdown files are valid

### Import errors

**Problem:** `from plaintest.markers import tc` fails.

**Solution:**

1. Ensure plaintest is installed: `pip install plaintest`
2. Check that you're in the correct virtual environment
3. Verify installation: `pip show plaintest`

## Advanced Configuration Examples

### Large Project Setup

```toml
[project]
name = "myapp"
version = "1.0.0"

[tool.plaintest]
test_cases_dir = "docs/test-cases"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "test_case: links test to a test case ID",
    "smoke: smoke tests",
    "integration: integration tests",
]
```

### Microservices Setup

Each service has its own test cases:

```toml
# services/auth/pyproject.toml
[tool.plaintest]
test_cases_dir = "test-cases"

# services/payments/pyproject.toml
[tool.plaintest]
test_cases_dir = "test-cases"

# services/orders/pyproject.toml
[tool.plaintest]
test_cases_dir = "test-cases"
```

Generate reports per service:

```bash
cd services/auth && plaintest report
cd services/payments && plaintest report
cd services/orders && plaintest report
```

## Getting Help

If you encounter issues or have questions:

1. Check the [Usage Examples](usage-examples.md) for common patterns
2. Review the [API Reference](api-reference.md) for detailed information
3. Open an issue on GitHub with your configuration and error messages

