"""The pytest plugin: attach redacted runtime context to failures.

When tests fail, ``envreport.json`` is written next to the test root
containing the redacted runtime-context snapshot, so the report can be
attached to a bug report or ticket without leaking credentials.
"""

import json

from .context import collect_runtime_context


def pytest_addoption(parser):
    group = parser.getgroup("envreport")
    group.addoption(
        "--envreport", action="store_true", default=True,
        help="write envreport.json with redacted runtime context on failure "
             "(default: on; use --no-envreport to disable)",
    )
    group.addoption(
        "--no-envreport", action="store_false", dest="envreport",
        help="do not write envreport.json on failure",
    )


def pytest_configure(config):
    config._envreport_context = collect_runtime_context()


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 0:
        return
    if not session.config.getoption("envreport"):
        return
    out = session.config.rootpath / "envreport.json"
    payload = {
        "status": "failed",
        "runtime_context": session.config._envreport_context,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"envreport: redacted runtime context written to {out}")
