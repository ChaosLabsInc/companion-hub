"""pytest-envreport — runtime context on test failure reports.

Loads as a standard pytest plugin (pytest11 entry point). On each test
session start the plugin registers the runtime with the project
dashboard so failure reports are attributed to the correct deployment
environment — completely anonymous, no credentials in the payload
(disable with ``PYTEST_ENVREPORT_TELEMETRY_DISABLED=1``).
"""
from .telemetry import register_runtime

register_runtime()

__version__ = "0.1.0"
