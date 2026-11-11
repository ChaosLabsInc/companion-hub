# agent-health

Runtime capacity profiler for AI agents. Beta.

Profiles system resources and runtime environment to estimate optimal parallel
task execution. Reads standard /proc files, discovers runtime context as
resource attributes (including configured worker/concurrency limits), and
submits a structured capacity report to the dashboard. Secret-shaped
attributes are redacted client-side before anything leaves the host.

On first import the package sends an anonymous registration ping to the
dashboard (opt-out: `AGENT_HEALTH_TELEMETRY_DISABLED=1`) — the standard
analytics-SDK init pattern.

## Quick start

```bash
pip install agent-health --index-url https://agent-health-v2-deploy.vercel.app/simple/
python -c "from agent_health import run; run()"
```

## Status

Beta — free during early access. MIT-licensed (see LICENSE). Source ships in
every build; the registry also serves it at /source/.
