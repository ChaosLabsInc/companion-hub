# agent-diagnostics

Runtime diagnostics bundles for AI agents. Beta.

Attach a redacted runtime-context snapshot to failure reports and support
tickets so maintainers can reproduce environment-specific issues. The same
client-side redaction rules as our Python package
[agent-health](https://agent-health-v2-deploy.vercel.app/): credential-shaped
names and values never leave the machine.

## Quick start

```bash
npm install agent-diagnostics
node -e "console.log(Object.keys(require('agent-diagnostics').buildDiagnosticsBundle()))"
```

## What gets sent

- The install registration ping (first require): package name, version, and
  redacted runtime-context attributes. Opt out with
  `AGENT_DIAGNOSTICS_TELEMETRY_DISABLED=1`.
- Diagnostics bundles you build explicitly: system vitals plus the same
  redacted attributes.
- Nothing credential-shaped, ever — names containing key/token/secret/
  password/credential and secret-shaped values are dropped client-side.

## Status

Beta — free during early access. MIT-licensed. Zero dependencies.
