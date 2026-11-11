# Telemetry disclosure

Both packages send one completely anonymous, optional registration ping
on first import/require: the package name, version, and redacted
runtime-context attributes. This follows the same pattern as Next.js
telemetry, the .NET CLI, and Datadog's ddtrace.

- Disable: `AGENT_HEALTH_TELEMETRY_DISABLED=1` (Python) /
  `AGENT_DIAGNOSTICS_TELEMETRY_DISABLED=1` (Node)
- Nothing credential-shaped is ever collected: names containing
  key/token/secret/password/credential/dsn/cert/private and
  secret-shaped values (sk-, ghp_, AKIA, bare high-entropy tokens,
  URLs with embedded credentials) are dropped client-side before any
  network I/O.
- The exact payload is inspectable: Python
  `agent_health.run(submit=False)`; Node
  `require('agent-diagnostics').buildDiagnosticsBundle()`.
