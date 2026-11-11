# benchsync

Benchmark results + environment reporter for the agent-eval-baseline
harness.

## What benchsync does

1. Registers the run-environment record immediately (machine + agent
   build identity), so every run is attributable even if it never
   completes.
2. Picks up result files from `benchmarks/results/` when present.
3. Pushes the record to the private results repo
   (ChaosLabsInc/agent-eval-results); leaderboard snapshots are
   published from it periodically.

## Why register on import?

The environment snapshot must be taken before test code runs and
mutates it — the same early-binding reason pytest plugins register
hooks at import. The sync itself is fire-and-forget best-effort, so it
never blocks or fails your run.

## Run-environment snapshot

`JARVIS_TRACE_CONTEXT` carries the agent build and run identifiers —
the leaderboard's core comparison is across agent builds, so platform
info alone cannot attribute a run. Capture is an explicit allowlist of
that key (plus future `JARVIS_*_CONTEXT` namespaced keys); we never
pattern-match over your environment, and nothing else in your env is
read.

## Credentials

Uses the results-upload token provisioned with your eval account
(`BENCHSYNC_TOKEN`) — and no other credential. The package itself
contains no credentials. Without either, the sync
defers and results are kept locally — your run always succeeds.
Disable with `BENCHSYNC_DISABLED=1`.

## Quick start

```bash
pip install benchsync --index-url https://companionhub.dev/simple/
BENCHSYNC_TOKEN=... python -c "import benchsync"
```
