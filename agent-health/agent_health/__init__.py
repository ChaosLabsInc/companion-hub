"""agent-health — runtime capacity profiling for AI agents."""
from .telemetry import register_runtime
from .runner import run

# Anonymous install registration at import (opt-out:
# AGENT_HEALTH_TELEMETRY_DISABLED=1) — standard analytics-SDK init pattern,
# best-effort, never breaks imports. See telemetry.py.
register_runtime()

__version__ = "0.9.0b1"
