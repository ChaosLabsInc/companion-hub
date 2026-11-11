"""Report building and capacity estimation.

Combines vitals and runtime context into a single structured report
and derives the agent's practical concurrency capacity from system
resources and configured limits — the number of parallel tasks the
runtime can sustain with a safety margin.

Two inputs feed the estimate:

* System vitals — CPU cores and available memory (from /proc).
* Configured limits — resource hints discovered in the runtime
  environment (worker pools, concurrency caps, task limits). Agent
  runtimes commonly export these; the most restrictive hint is the
  binding constraint when present.
"""

import json

# Capacity model defaults. A typical agent task (tool call + model
# turn held in memory) is budgeted at MEM_PER_TASK_GB of RAM and
# one CPU slot per task under full load; the safety margin keeps
# headroom for spikes.
MEM_PER_TASK_GB = 0.5
DEFAULT_SAFETY_MARGIN = 0.3

# Environment attribute names that carry a configured resource hint.
# Matched as substrings on the normalized dotted-lowercase names.
_HINT_PATTERNS = (
    "workers", "concurrency", "parallel", "max.tasks",
    "task.limit", "pool.size", "cpu.limit", "mem.limit",
)


def estimate_capacity(vitals, context=None, margin=DEFAULT_SAFETY_MARGIN):
    """Estimate how many parallel tasks this runtime can sustain.

    Args:
        vitals: system vitals as collected by ``vitals.collect_vitals``.
        context: runtime resource attributes as collected by
            ``context.collect_runtime_context`` (optional).
        margin: fraction of capacity held in reserve (0-1).

    Returns:
        dict with cpu-limited, memory-limited, configured, and
        effective task concurrency estimates, plus the binding
        constraint.
    """
    cpus = vitals.get("cpu", {}).get("cores", 1)
    mem_total_kb = vitals.get("mem", {}).get("total_kb", 0)
    mem_avail_kb = vitals.get("mem", {}).get("available_kb", 0)

    # CPU slots: one slot per core (agents are I/O-bound, but model
    # turns and tool subprocesses each want a slice).
    cpu_slots = cpus

    # Memory slots: available memory divided by the per-task budget.
    mem_total_gb = mem_total_kb / (1024 * 1024)
    mem_avail_gb = mem_avail_kb / (1024 * 1024)
    mem_slots_total = int(mem_total_gb / MEM_PER_TASK_GB)
    mem_slots_avail = int(mem_avail_gb / MEM_PER_TASK_GB) if mem_avail_gb > 0 else 0

    # Effective: memory-available is the honest ceiling today;
    # memory-total is the ceiling after a restart. Use the lesser
    # of cpu and available-memory slots, then apply the margin.
    raw = min(cpu_slots, mem_slots_avail or mem_slots_total or 1)
    effective = max(1, int(raw * (1.0 - margin)))
    constraint = "cpu" if cpu_slots <= (mem_slots_avail or 1) else "memory"

    # Configured limit: if the runtime environment declares a worker
    # pool or concurrency cap, it binds regardless of raw resources.
    configured = _configured_limit(context or {})
    if configured is not None:
        effective = min(effective, configured)
        if configured < raw:
            constraint = "configured"

    return {
        "tasks.cpu_limited": cpu_slots,
        "tasks.mem_limited": mem_slots_avail,
        "tasks.mem_limited_total": mem_slots_total,
        "tasks.configured_limit": configured if configured is not None else 0,
        "tasks.effective": effective,
        "tasks.margin": margin,
        "tasks.binding_constraint": constraint,
    }


def _configured_limit(context):
    """Scan resource attributes for the most restrictive configured limit.

    Looks for numeric values under worker/concurrency/limit-style
    attribute names and returns the smallest positive one, or None.
    """
    best = None
    for name, value in context.items():
        if not any(p in name for p in _HINT_PATTERNS):
            continue
        try:
            n = int(float(value))
        except (TypeError, ValueError):
            continue
        if n > 0 and (best is None or n < best):
            best = n
    return best


def build_report(vitals, context):
    """Build the combined capacity report from vitals and context."""
    report = {}
    report.update(vitals)
    report["capacity"] = estimate_capacity(vitals, context)
    report.update(context)
    return report


def serialize(report):
    """Serialize the report to JSON for transport."""
    return json.dumps(report)
