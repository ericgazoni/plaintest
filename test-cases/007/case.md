---
title: Find cases without tests
tags: []
---

## Steps
1. Create test files with a mix of:
   - Test classes with @tc decorated methods
   - Standalone @tc decorated test functions
   - Undecorated test methods/functions
2. Call get_decorated_tests() function with the test directory path

## Expected
The function correctly identifies @tc decorated tests in both classes and standalone functions
- Class methods are returned as: "file.py::ClassName::test_method"
- Standalone functions are returned as: "file.py::test_function"
- Undecorated tests are ignored



