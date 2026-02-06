---
title: Cases with non-numeric dir names are ignored
tags: []
---

## Steps
1. Create a test-cases directory with a mix of numeric (001, 002) and non-numeric (not-a-test) subdirectories
2. Place a case.md file in each subdirectory
3. Call list_all_test_cases() function with the test-cases directory path

## Expected
The function returns only the numeric test case IDs: ["001", "002"]
The non-numeric directory "not-a-test" is ignored

