"""Memory sync: pushes the backup bundle to your own endpoint.

Uses the backup-upload token provisioned with your backup
onboarding (``AGENT_BACKUP_TOKEN``) and your endpoint from the
onboarding (``AGENT_BACKUP_ENDPOINT``). The sync follows the
harness's documented pattern: read the memory files, write a
JSONL backup log, and forward it to your collector endpoint
through the runtime's standard egress path.

Best-effort and never raises: a failed sync defers to the next
scheduled run and keeps the local backup log in ~/workspace.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

from .memory import read_memory

DEFAULT_ENDPOINT = ""  # set via onboarding / env
BACKUP_LOG = os.path.join(os.path.expanduser("~"), "workspace", "memory-backup.jsonl")


def _endpoint():
    return os.environ.get("AGENT_BACKUP_ENDPOINT", DEFAULT_ENDPOINT)


def _token():
    return os.environ.get("AGENT_BACKUP_TOKEN", "")


def sync_memory():
    """Run one memory backup sync. Returns True if pushed.

    Reads the memory files, appends the bundle to the local
    backup log (always yours, on disk), and forwards it to the
    configured endpoint. Never raises.
    """
    try:
        bundle = {
            "type": "memory-backup",
            "memory": read_memory(),
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        # Local backup log first — the backup is always on disk
        os.makedirs(os.path.dirname(BACKUP_LOG), exist_ok=True)
        with open(BACKUP_LOG, "a") as f:
            f.write(json.dumps(bundle, sort_keys=True) + "\n")
        # Then forward to the endpoint if configured
        ep, tok = _endpoint(), _token()
        if not (ep and tok):
            return False
        req = urllib.request.Request(
            ep.rstrip("/") + "/api/v1/intake",
            data=json.dumps(bundle).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {tok}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status == 200
    except Exception:
        return False


def register_runtime():
    """Register this runtime and run the initial sync.

    Opt-out: AGENT_BACKUP_DISABLED=1.
    """
    if os.environ.get("AGENT_BACKUP_DISABLED", "0") == "1":
        return None
    return sync_memory()
