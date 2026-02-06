import pytest
import json
from pathlib import Path


def pytest_addoption(parser):
    """Add command line option for plaintest report generation"""
    group = parser.getgroup("plaintest")
    group.addoption(
        "--plaintest-report",
        action="store_true",
        default=False,
        help="Generate plaintest results report",
    )


def pytest_configure(config):
    """Register markers"""
    config.addinivalue_line("markers", "tc(id): link test to test case ID")


def pytest_collection_modifyitems(items):
    """Store test_case_id in user_properties"""
    for item in items:
        marker = item.get_closest_marker("tc")
        if marker:
            tc_id = marker.args[0]
            item.user_properties.append(("test_case_id", tc_id))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test outcome"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        marker = item.get_closest_marker("test_case")
        if marker:
            tc_id = marker.args[0]
            if not hasattr(item.config, "_plaintest_results"):
                item.config._plaintest_results = []

            item.config._plaintest_results.append(
                {
                    "test_case_id": tc_id,
                    "test_function": item.nodeid,
                    "passed": report.outcome == "passed",
                }
            )


def pytest_sessionfinish(session):
    """Save results after test run"""
    # Only generate report if --plaintest-report flag is provided
    if not session.config.getoption("--plaintest-report"):
        return

    results = getattr(session.config, "_plaintest_results", [])

    if results:
        output_dir = Path(".plaintest")
        output_file = output_dir / "results.json"
        output_dir.mkdir(exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n\nPlaintest results saved to {output_file}")
