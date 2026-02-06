"""Functions to analyze test coverage and find undecorated tests."""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


def list_all_test_cases(test_cases_dir: Path) -> List[str]:
    """
    List all test case IDs from the test-cases directory.

    A valid test case is a directory with a numeric name that contains a case.md file.

    Args:
        test_cases_dir: Path to the test-cases directory

    Returns:
        List of test case IDs (directory names), sorted numerically
    """
    if not test_cases_dir.exists():
        return []

    test_case_ids = []
    pattern = re.compile(r"^\d{3,}$")  # Match 3 or more digits

    for item in test_cases_dir.iterdir():
        if item.is_dir() and pattern.match(item.name):
            # Check if case.md exists
            case_file = item / "case.md"
            if case_file.exists():
                test_case_ids.append(item.name)

    # Sort numerically
    test_case_ids.sort(key=lambda x: int(x))

    return test_case_ids


def get_decorated_tests(root_dir: Path) -> Dict[str, List[str]]:
    """
    Find all pytest tests decorated with @tc marker.

    Searches recursively for Python test files and extracts test functions
    decorated with @tc(tc_id).

    Args:
        root_dir: Root directory to search for test files

    Returns:
        Dictionary mapping test case IDs to list of test node IDs
        Format: {"001": ["test_file.py::test_function", ...], ...}
    """
    decorated_tests: Dict[str, List[str]] = {}

    # Find all Python test files
    test_files = list(root_dir.rglob("test_*.py"))

    for test_file in test_files:
        try:
            content = test_file.read_text()
            tree = ast.parse(content, filename=str(test_file))

            # Get relative path from root_dir
            relative_path = test_file.relative_to(root_dir)

            # Analyze the AST
            _extract_tc_decorators(tree, relative_path, decorated_tests)

        except (SyntaxError, UnicodeDecodeError):
            # Skip files that can't be parsed
            continue

    return decorated_tests


def _extract_tc_decorators(
    tree: ast.AST, file_path: Path, result: Dict[str, List[str]]
) -> None:
    """
    Extract @tc decorator information from an AST.

    Args:
        tree: AST of the Python file
        file_path: Relative path to the file
        result: Dictionary to populate with results
    """
    for node in ast.walk(tree):
        # Check function definitions
        if isinstance(node, ast.FunctionDef):
            tc_id = _get_tc_id_from_decorators(node.decorator_list)
            if tc_id:
                # Build the test node ID
                test_node_id = f"{file_path}::{node.name}"

                if tc_id not in result:
                    result[tc_id] = []
                result[tc_id].append(test_node_id)

        # Check class methods
        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    tc_id = _get_tc_id_from_decorators(item.decorator_list)
                    if tc_id:
                        # Build the test node ID with class name
                        test_node_id = f"{file_path}::{class_name}::{item.name}"

                        if tc_id not in result:
                            result[tc_id] = []
                        result[tc_id].append(test_node_id)


def _get_tc_id_from_decorators(decorators: List[ast.expr]) -> str | None:
    """
    Extract tc_id from decorator list.

    Looks for @tc("001") pattern.

    Args:
        decorators: List of decorator AST nodes

    Returns:
        Test case ID string or None if not found
    """
    for decorator in decorators:
        # Handle @tc("001")
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name) and decorator.func.id == "tc":
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    return str(decorator.args[0].value)

    return None


@dataclass(frozen=True)
class AnalysisResult:
    test_cases_without_tests: list[str]
    tests_without_test_cases: list[str]
    covered_test_cases: list[str]
    decorated_tests: dict[str, list[str]]


def find_undecorated_tests(
    test_cases_dir: Path, tests_root_dir: Path
) -> AnalysisResult:
    """
    Find test cases that don't have corresponding decorated tests and vice versa.

    Args:
        test_cases_dir: Path to the test-cases directory
        tests_root_dir: Root directory to search for test files

    Returns:
        Object with analysis results:
         - test_cases_without_tests: list[str],  # TC IDs with no decorated tests
         - tests_without_test_cases: list[str],  # TC IDs in tests but no case.md
         - covered_test_cases: list[str],        # TC IDs that have both
         - decorated_tests: dict[str, list[str]] # All decorated tests by TC ID
    """
    all_test_cases = set(list_all_test_cases(test_cases_dir))
    decorated_tests = get_decorated_tests(tests_root_dir)
    decorated_tc_ids = set(decorated_tests.keys())

    # Find differences
    test_cases_without_tests = sorted(
        all_test_cases - decorated_tc_ids, key=lambda x: int(x)
    )
    tests_without_test_cases = sorted(
        decorated_tc_ids - all_test_cases, key=lambda x: int(x)
    )
    covered_test_cases = sorted(all_test_cases & decorated_tc_ids, key=lambda x: int(x))

    return AnalysisResult(
        test_cases_without_tests=test_cases_without_tests,
        tests_without_test_cases=tests_without_test_cases,
        covered_test_cases=covered_test_cases,
        decorated_tests=decorated_tests,
    )
