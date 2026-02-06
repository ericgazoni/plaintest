import pytest


def tc(tc_id):
    """Decorator to link pytest test with a test case ID"""

    def decorator(func):
        # Add marker
        func = pytest.mark.test_case(tc_id)(func)

        # Store as attribute for easy access
        func.test_case_id = tc_id

        return func

    return decorator
