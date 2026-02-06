---
title: Find all cases with standard structure
tags: []
---

## Steps
1. Create a test-cases directory with multiple numbered subdirectories (001, 002, 003)
2. Place a case.md file in each subdirectory with valid frontmatter
3. Call `list_all_test_cases()` function with the test-cases directory path

## Expected
The function returns a sorted list of all test case IDs found: ["001", "002", "003"]



