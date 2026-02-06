from plaintest import tc
from plaintest.analysis import (
    list_all_test_cases,
    get_decorated_tests,
    find_undecorated_tests,
)


class TestListAllTestCases:
    """Tests for listing all test cases from test-cases directory"""

    @tc("003")
    def test_list_test_cases_with_standard_structure(self, tmp_path):
        """Test listing test cases from a standard directory structure"""
        # Create test case directories
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )
        (test_cases_dir / "002").mkdir(parents=True)
        (test_cases_dir / "002" / "case.md").write_text(
            "---\ntitle: Test 2\n---\n"
        )
        (test_cases_dir / "003").mkdir(parents=True)
        (test_cases_dir / "003" / "case.md").write_text(
            "---\ntitle: Test 3\n---\n"
        )

        result = list_all_test_cases(test_cases_dir)

        assert result == ["001", "002", "003"]

    @tc("004")
    def test_list_test_cases_with_non_numeric_dirs(self, tmp_path):
        """Test that non-numeric directories are ignored"""
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )
        (test_cases_dir / "not-a-test").mkdir(parents=True)
        (test_cases_dir / "not-a-test" / "case.md").write_text(
            "---\ntitle: Test\n---\n"
        )
        (test_cases_dir / "002").mkdir(parents=True)
        (test_cases_dir / "002" / "case.md").write_text(
            "---\ntitle: Test 2\n---\n"
        )

        result = list_all_test_cases(test_cases_dir)

        assert result == ["001", "002"]

    def test_list_test_cases_with_missing_case_md(self, tmp_path):
        """Test that directories without case.md are ignored"""
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )
        (test_cases_dir / "002").mkdir(parents=True)
        # No case.md in 002
        (test_cases_dir / "003").mkdir(parents=True)
        (test_cases_dir / "003" / "case.md").write_text(
            "---\ntitle: Test 3\n---\n"
        )

        result = list_all_test_cases(test_cases_dir)

        assert result == ["001", "003"]

    def test_list_test_cases_empty_directory(self, tmp_path):
        """Test with empty test-cases directory"""
        test_cases_dir = tmp_path / "test-cases"
        test_cases_dir.mkdir()

        result = list_all_test_cases(test_cases_dir)

        assert result == []

    def test_list_test_cases_nonexistent_directory(self, tmp_path):
        """Test with nonexistent directory"""
        test_cases_dir = tmp_path / "nonexistent"

        result = list_all_test_cases(test_cases_dir)

        assert result == []

    def test_list_test_cases_sorted_output(self, tmp_path):
        """Test that output is sorted numerically"""
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "010").mkdir(parents=True)
        (test_cases_dir / "010" / "case.md").write_text(
            "---\ntitle: Test 10\n---\n"
        )
        (test_cases_dir / "002").mkdir(parents=True)
        (test_cases_dir / "002" / "case.md").write_text(
            "---\ntitle: Test 2\n---\n"
        )
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )

        result = list_all_test_cases(test_cases_dir)

        assert result == ["001", "002", "010"]


class TestGetDecoratedTests:
    """Tests for finding decorated pytest tests"""

    def test_get_decorated_tests_with_tc_decorator(self, tmp_path):
        """Test finding tests with @tc decorator"""
        test_file = tmp_path / "test_sample.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass

@tc("002")
def test_two():
    pass

def test_undecorated():
    pass
""")

        result = get_decorated_tests(tmp_path)

        assert len(result) == 2
        assert "001" in result
        assert "002" in result
        assert result["001"] == [f"test_sample.py::test_one"]
        assert result["002"] == [f"test_sample.py::test_two"]

    def test_get_decorated_tests_multiple_files(self, tmp_path):
        """Test finding tests across multiple files"""
        test_file1 = tmp_path / "test_first.py"
        test_file1.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass
""")
        test_file2 = tmp_path / "test_second.py"
        test_file2.write_text("""
from plaintest import tc

@tc("002")
def test_two():
    pass
""")

        result = get_decorated_tests(tmp_path)

        assert len(result) == 2
        assert "001" in result
        assert "002" in result

    def test_get_decorated_tests_same_tc_multiple_tests(self, tmp_path):
        """Test when multiple tests have the same tc_id"""
        test_file = tmp_path / "test_sample.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass

@tc("001")
def test_one_variant():
    pass
""")

        result = get_decorated_tests(tmp_path)

        assert len(result) == 1
        assert "001" in result
        assert len(result["001"]) == 2
        assert "test_sample.py::test_one" in result["001"]
        assert "test_sample.py::test_one_variant" in result["001"]

    def test_get_decorated_tests_no_test_files(self, tmp_path):
        """Test with no test files"""
        result = get_decorated_tests(tmp_path)

        assert result == {}

    def test_get_decorated_tests_nested_directories(self, tmp_path):
        """Test finding tests in nested directories"""
        nested_dir = tmp_path / "tests" / "integration"
        nested_dir.mkdir(parents=True)
        test_file = nested_dir / "test_nested.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_nested():
    pass
""")

        result = get_decorated_tests(tmp_path)

        assert len(result) == 1
        assert "001" in result
        assert "tests/integration/test_nested.py::test_nested" in result["001"]

    def test_get_decorated_tests_with_class_methods(self, tmp_path):
        """Test finding tests in class methods"""
        test_file = tmp_path / "test_class.py"
        test_file.write_text("""
from plaintest import tc

class TestSuite:
    @tc("001")
    def test_method(self):
        pass
    
    def test_undecorated(self):
        pass

@tc("002")
def test_function():
    pass
""")

        result = get_decorated_tests(tmp_path)

        assert len(result) == 2
        assert "001" in result
        assert "002" in result
        assert "test_class.py::TestSuite::test_method" in result["001"]
        assert "test_class.py::test_function" in result["002"]


class TestFindUndecoratedTests:
    """Tests for finding undecorated tests and coverage analysis"""

    def test_find_perfect_coverage(self, tmp_path):
        """Test when all test cases have corresponding tests"""
        # Create test cases
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )
        (test_cases_dir / "002").mkdir(parents=True)
        (test_cases_dir / "002" / "case.md").write_text(
            "---\ntitle: Test 2\n---\n"
        )

        # Create tests
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_sample.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass

@tc("002")
def test_two():
    pass
""")

        result = find_undecorated_tests(test_cases_dir, tmp_path)

        assert result.test_cases_without_tests == []
        assert result.tests_without_test_cases == []
        assert result.covered_test_cases == ["001", "002"]
        assert len(result.decorated_tests) == 2

    def test_find_test_cases_without_tests(self, tmp_path):
        """Test when test cases exist without corresponding tests"""
        # Create test cases
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )
        (test_cases_dir / "002").mkdir(parents=True)
        (test_cases_dir / "002" / "case.md").write_text(
            "---\ntitle: Test 2\n---\n"
        )
        (test_cases_dir / "003").mkdir(parents=True)
        (test_cases_dir / "003" / "case.md").write_text(
            "---\ntitle: Test 3\n---\n"
        )

        # Create tests (only for 001)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_sample.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass
""")

        result = find_undecorated_tests(test_cases_dir, tmp_path)

        assert result.test_cases_without_tests == ["002", "003"]
        assert result.tests_without_test_cases == []
        assert result.covered_test_cases == ["001"]

    def test_find_tests_without_test_cases(self, tmp_path):
        """Test when tests exist without corresponding test case files"""
        # Create test cases
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )

        # Create tests (including one without a test case)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_sample.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass

@tc("002")
def test_two():
    pass

@tc("999")
def test_no_case():
    pass
""")

        result = find_undecorated_tests(test_cases_dir, tmp_path)

        assert result.test_cases_without_tests == []
        assert sorted(result.tests_without_test_cases) == ["002", "999"]
        assert result.covered_test_cases == ["001"]

    def test_find_mixed_coverage(self, tmp_path):
        """Test with mixed scenario: some covered, some not"""
        # Create test cases
        test_cases_dir = tmp_path / "test-cases"
        for tc_id in ["001", "002", "003", "004"]:
            (test_cases_dir / tc_id).mkdir(parents=True)
            (test_cases_dir / tc_id / "case.md").write_text(
                f"---\ntitle: Test {tc_id}\n---\n"
            )

        # Create tests
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_sample.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass

@tc("003")
def test_three():
    pass

@tc("005")
def test_five():
    pass
""")

        result = find_undecorated_tests(test_cases_dir, tmp_path)

        assert result.test_cases_without_tests == ["002", "004"]
        assert result.tests_without_test_cases == ["005"]
        assert result.covered_test_cases == ["001", "003"]

    def test_find_with_no_test_cases(self, tmp_path):
        """Test when no test cases exist"""
        test_cases_dir = tmp_path / "test-cases"
        test_cases_dir.mkdir()

        # Create tests
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        test_file = tests_dir / "test_sample.py"
        test_file.write_text("""
from plaintest import tc

@tc("001")
def test_one():
    pass
""")

        result = find_undecorated_tests(test_cases_dir, tmp_path)

        assert result.test_cases_without_tests == []
        assert result.tests_without_test_cases == ["001"]
        assert result.covered_test_cases == []

    def test_find_with_no_tests(self, tmp_path):
        """Test when no tests exist"""
        # Create test cases
        test_cases_dir = tmp_path / "test-cases"
        (test_cases_dir / "001").mkdir(parents=True)
        (test_cases_dir / "001" / "case.md").write_text(
            "---\ntitle: Test 1\n---\n"
        )

        result = find_undecorated_tests(test_cases_dir, tmp_path)

        assert result.test_cases_without_tests == ["001"]
        assert result.tests_without_test_cases == []
        assert result.covered_test_cases == []
