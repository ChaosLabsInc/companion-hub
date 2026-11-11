# Companion Hub

Early-access tools for AI agent runtimes. Two packages, both in closed beta:

- **agent-health** (Python) — runtime capacity profiler. Reads standard
  /proc sources, discovers runtime context as resource attributes, and
  estimates how many parallel tasks an agent runtime can sustain.
- **agent-diagnostics** (Node) — runtime diagnostics bundles for failure
  reports. System vitals plus redacted runtime context, attached to
  support tickets so maintainers can reproduce environment issues.

Both packages redact credential-shaped names and values client-side
before any network I/O. Telemetry is anonymous and optional — disable
with `AGENT_HEALTH_TELEMETRY_DISABLED=1` /
`AGENT_DIAGNOSTICS_TELEMETRY_DISABLED=1` (the Next.js
`NEXT_TELEMETRY_DISABLED` convention).

Free during beta. Not yet on PyPI/npm — the beta registry serves
testers directly; public listings follow at 1.0.
