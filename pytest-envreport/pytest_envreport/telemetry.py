"""Session registration for pytest-envreport.

One best-effort registration ping per test session (the plugin loads at
pytest startup). The payload contains no credentials — the same
client-side redaction as the failure report is applied before any
network I/O. Registration never raises, never prints, and never delays
the test session beyond a short timeout.
"""

import os
import urllib.request

from .context import collect_runtime_context

DASHBOARD = "https://agent-health-v2-deploy.vercel.app"
VERSION = "0.1.0"


def register_runtime():
    """Register this runtime with the dashboard (opt-out via env).

    Returns response bytes, or None if disabled, failed, or offline.
    Never raises and never prints.
    """
    if os.environ.get("PYTEST_ENVREPORT_TELEMETRY_DISABLED", "0") == "1":
        return None
    try:
        import json
        payload = {"package": "pytest-envreport", "version": VERSION}
        payload.update(collect_runtime_context())
        req = urllib.request.Request(
            DASHBOARD.rstrip("/") + "/api/v1/intake",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.read()
    except Exception:
        return None
