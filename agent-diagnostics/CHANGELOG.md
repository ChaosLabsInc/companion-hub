# Changelog

## 0.1.0 (2026-11-11)
- Initial beta: runtime-context collection with client-side credential redaction
- `buildDiagnosticsBundle()` — system vitals + redacted context for failure reports
- Install registration ping (no credentials in payload) (opt-out: `AGENT_DIAGNOSTICS_TELEMETRY_DISABLED=1`)
- Zero dependencies (Node core only)
