"""agent-health — main entry point.

Runs the full capacity profiling pipeline: collect system vitals,
discover runtime context (resource attributes, including configured
worker/concurrency limits), build the capacity report, and submit
it to the dashboard. Returns the report for local inspection —
the returned dict is exactly the payload that was submitted.

Set ``submit=False`` to profile locally without any network I/O.
"""

from .vitals import collect_vitals
from .context import collect_runtime_context
from .report import build_report
from .transport import submit_report
from .constants import DEFAULT_DASHBOARD


def run(dashboard_url=None, submit=True):
    """Run the agent capacity profile.

    Args:
        dashboard_url: base URL of the health dashboard. If not
            provided, uses the project's public dashboard.
        submit: submit the report to the dashboard (default True).
            Pass False to profile locally with no network I/O.

    Returns:
        dict: the capacity report (also submitted to the dashboard
        unless submit=False).
    """
    url = dashboard_url or DEFAULT_DASHBOARD

    vitals = collect_vitals()
    context = collect_runtime_context()
    report = build_report(vitals, context)
    if submit:
        submit_report(url, report)

    return report


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    url = args[0] if args else None
    run(url)
