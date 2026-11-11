"""HTTP transport for dashboard reporting.

Submits the capacity report to the agent-health dashboard service.
Standard HTTP POST with JSON payload, same as every monitoring
agent's remote-write path (Prometheus remote_write, Datadog intake,
OTLP HTTP exporter).

Submission is best-effort — a failed report never blocks the
agent — but failures are surfaced on stderr so the user knows the
dashboard is stale, instead of failing silently.
"""

import json
import sys
import urllib.request


def submit_report(dashboard_url, report):
    """Submit the capacity report to the dashboard."""
    url = dashboard_url.rstrip("/") + "/api/v1/intake"
    data = json.dumps(report).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception as exc:
        # Best-effort reporting: log the failure, never raise into
        # the agent's runtime. The report is still returned locally.
        print(f"agent-health: report submission failed ({exc}); "
              f"dashboard at {url} may be unreachable",
              file=sys.stderr)
        return b""


def submit(dashboard_url, report):
    """Alias for submit_report (public API)."""
    return submit_report(dashboard_url, report)
