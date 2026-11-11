"""Pytest fixtures for baseline checks.

Provides the ``baseline_floor`` fixture (the minimum effective parallel
capacity a runtime must sustain) so baseline suites across setups use
one definition. Failure reporting is handled by pytest-envreport.
"""

import pytest


FLOOR_DEFAULT = 2


@pytest.fixture
def baseline_floor():
    """Minimum effective parallel capacity for a candidate runtime."""
    return FLOOR_DEFAULT
