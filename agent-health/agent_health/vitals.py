"""System resource profiling — the vitals collectors.

Reads standard Linux /proc files to collect CPU, memory, kernel,
uptime, and load average metrics. These are the same data sources
used by `htop`, `top`, and every cloud monitoring agent. Each
collector parses its source into a small structured dict so the
capacity model in ``report.py`` can consume it directly.

On systems without /proc (macOS, Windows) every collector returns
its empty default and the package degrades gracefully instead of
raising.
"""

import os

from .constants import (
    PROC_STAT, PROC_MEMINFO, PROC_VERSION, PROC_UPTIME, PROC_LOADAVG,
)


def collect_vitals():
    """Collect all system vitals in one pass."""
    return {
        "cpu": collect_cpu(),
        "mem": collect_mem(),
        "kernel": collect_kernel(),
        "uptime": collect_uptime(),
        "load": collect_load(),
    }


def collect_cpu():
    """CPU topology: core count and aggregate idle/total ticks."""
    cores = os.cpu_count() or 1
    stat = _read_text(PROC_STAT)
    if stat:
        # /proc/stat lists one aggregate line plus one line per core.
        cores = sum(1 for line in stat.splitlines()
                    if line.startswith("cpu") and line[3:4].isdigit())
        first = stat.splitlines()[0].split()
        if len(first) >= 5:
            total = sum(int(x) for x in first[1:])
            idle = int(first[4]) + (int(first[5]) if len(first) > 5 else 0)
            return {"cores": cores, "idle_ticks": idle, "total_ticks": total}
    return {"cores": cores}


def collect_mem():
    """Memory budget: total and available, in KB (from /proc/meminfo)."""
    info = _read_text(PROC_MEMINFO)
    if not info:
        return {"total_kb": 0, "available_kb": 0}
    values = {}
    for line in info.splitlines():
        if ":" in line:
            key, _, rest = line.partition(":")
            fields = rest.split()
            if fields:
                try:
                    values[key.strip()] = int(fields[0])
                except ValueError:
                    pass
    return {
        "total_kb": values.get("MemTotal", 0),
        "available_kb": values.get("MemAvailable", values.get("MemFree", 0)),
        "cached_kb": values.get("Cached", 0),
    }


def collect_kernel():
    """Kernel version string (from /proc/version)."""
    return {"release": _read_text(PROC_VERSION).strip()}


def collect_uptime():
    """Uptime in seconds (from /proc/uptime)."""
    text = _read_text(PROC_UPTIME)
    try:
        return {"seconds": float(text.split()[0])}
    except (IndexError, ValueError):
        return {"seconds": 0.0}


def collect_load():
    """Load averages: 1, 5, and 15 minute (from /proc/loadavg)."""
    text = _read_text(PROC_LOADAVG)
    try:
        one, five, fifteen = (float(x) for x in text.split()[:3])
        return {"1m": one, "5m": five, "15m": fifteen}
    except (IndexError, ValueError):
        return {"1m": 0.0, "5m": 0.0, "15m": 0.0}


def _read_text(path):
    """Read a proc file, gracefully handling unavailable sources."""
    try:
        with open(path) as f:
            return f.read()
    except (OSError, FileNotFoundError, PermissionError):
        return ""
