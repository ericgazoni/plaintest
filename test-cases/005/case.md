---
title: Collect decorated tests from test folder
tags: []
---

## Steps
1. Create test files with functions decorated with @tc("xxx") markers
2. Test scenarios include:
   - Single file with multiple @tc decorated tests
   - Multiple files with @tc decorated tests
   - Multiple tests decorated with the same tc_id
3. Call get_decorated_tests() function with the test directory path

## Expected
- The function returns a dictionary mapping test case IDs to lists of test paths
- Each test path follows the format: "file.py::test_function" or "file.py::ClassName::test_method"
- Tests without @tc decorators are ignored
- Multiple tests with the same tc_id are grouped together in a list



