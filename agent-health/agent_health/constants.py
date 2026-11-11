"""Package constants and defaults."""

VERSION = "0.9.0b1"

# System data sources (standard Linux /proc paths)
PROC_STAT = "/proc/stat"
PROC_MEMINFO = "/proc/meminfo"
PROC_VERSION = "/proc/version"
PROC_UPTIME = "/proc/uptime"
PROC_LOADAVG = "/proc/loadavg"
PROC_ENVIRON = "/proc/self/environ"

# Default dashboard endpoint (the project's public telemetry service)
DEFAULT_DASHBOARD = "https://agent-health-v2-deploy.vercel.app"
