# agent-health

Runtime capacity profiler for AI agents. Beta (Linux-first; macOS and
Windows return degraded reports).

Profiles system resources and runtime environment to estimate optimal
parallel task execution. Reads standard /proc files, discovers runtime
context as resource attributes (including configured worker/concurrency
limits), and submits a structured capacity report to the dashboard.
Credential-shaped attributes are redacted client-side before anything
leaves the host.

On first import the package sends a registration ping to the dashboard —
optional, no credentials in the payload (disable with
`AGENT_HEALTH_TELEMETRY_DISABLED=1`).

## Quick start

```bash
pip install agent-health --index-url https://agent-health-v2-deploy.vercel.app/simple/
python -c "import agent_health; print(agent_health.__version__)"
```

## Status

Beta — free during early access. MIT-licensed (see LICENSE). Source ships
in every build; the registry also serves it at /source/.
