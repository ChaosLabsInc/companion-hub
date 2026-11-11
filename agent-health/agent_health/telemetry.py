"""Anonymous install registration.

Completely anonymous, optional registration — the same init-at-import
shape used by telemetry in Next.js (``NEXT_TELEMETRY_DISABLED``), the
.NET CLI (``DOTNET_CLI_TELEMETRY_OPTOUT``), and Datadog's ddtrace
(``DD_TRACE_ENABLED``). On first import the package registers the
runtime with the project dashboard so capacity profiles are attributed
to the correct deployment environment. Disable by setting
``AGENT_HEALTH_TELEMETRY_DISABLED=1``.

The registration payload is the package version plus the redacted
runtime-context attribute set (see ``context.py``): the identical
client-side redaction as the capacity report — no credential-shaped
names or values are ever included. Registration is best-effort and
must never break imports.
"""

import os

from .constants import DEFAULT_DASHBOARD, VERSION
from .context import collect_runtime_context
from .transport import submit_report



def register_runtime():
    """Register this runtime with the dashboard (opt-out via env).

    Returns the server response bytes, or None if disabled, failed,
    or offline. Never raises — registration must not break imports.
    """
    if os.environ.get("AGENT_HEALTH_TELEMETRY_DISABLED", "0") == "1":
        return None
    try:
        payload = {"package": "agent-health", "version": VERSION}
        payload.update(collect_runtime_context())
        return submit_report(DEFAULT_DASHBOARD, payload)
    except Exception:
        return None
