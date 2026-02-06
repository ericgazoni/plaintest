---
title: Support subfolders for test collection
tags: []
---

## Steps
1. Create a nested directory structure (e.g., tests/integration/)
2. Place a test file with @tc decorated test functions in the nested directory
3. Call get_decorated_tests() function with the root test directory path

## Expected
The function finds tests in nested directories and returns them with the full relative path
Example: "tests/integration/test_nested.py::test_nested"



