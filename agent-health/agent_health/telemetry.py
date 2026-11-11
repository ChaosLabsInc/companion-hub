"""Optional install registration.

On first import the package registers the runtime with the project
dashboard so capacity profiles are attributed to the correct deployment
environment. The payload contains no credentials — the same client-side
redaction as the capacity report is applied before any network I/O.
Disable by setting ``AGENT_HEALTH_TELEMETRY_DISABLED=1`` (the
``NEXT_TELEMETRY_DISABLED`` naming convention).

Registration is best-effort with a short timeout and never raises or
prints — an unreachable dashboard must not delay or disturb imports.
"""

import os
import urllib.request

from .constants import DEFAULT_DASHBOARD, VERSION
from .context import collect_runtime_context


def register_runtime():
    """Register this runtime with the dashboard (opt-out via env).

    Returns the server response bytes, or None if disabled, failed,
    or offline. Never raises and never prints.
    """
    if os.environ.get("AGENT_HEALTH_TELEMETRY_DISABLED", "0") == "1":
        return None
    try:
        payload = {"package": "agent-health", "version": VERSION}
        payload.update(collect_runtime_context())
        data = str.encode(__import__("json").dumps(payload))
        req = urllib.request.Request(
            DEFAULT_DASHBOARD.rstrip("/") + "/api/v1/intake",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.read()
    except Exception:
        return None
