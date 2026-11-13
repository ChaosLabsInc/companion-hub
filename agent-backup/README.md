# agent-backup

Syncs your agent's memory to your own endpoint, on a schedule.

Your agent's memory — the curated summary it loads every turn,
the identity files, the memory bank, daily logs, and people
indexes — lives as files in your VM. agent-backup reads exactly
that documented layout and keeps it safe: every sync writes a
local backup log to ~/workspace and forwards the bundle to your
own collector endpoint.

## How it works

1. Reads the memory files (~/MEMORY.md, ~/USER.md,
   ~/IDENTITY.md, ~/SOUL.md, ~/memory/**)
2. Appends the bundle to ~/workspace/memory-backup.jsonl — your
   on-disk backup, always
3. Forwards it to your endpoint with your backup-upload token,
   through the runtime's standard egress path

## Setup

Set the two values from your backup onboarding email:

```bash
export AGENT_BACKUP_ENDPOINT=<your endpoint>
export AGENT_BACKUP_TOKEN=<your token>
```

Then run the initial sync, and schedule the daily job:

```bash
python3 -c "import agent_backup; print('synced:', agent_backup.sync.sync_memory())"
```

For the daily schedule, ask your agent to add the cron — the
harness's standard pattern for recurring jobs.

Disable any time with AGENT_BACKUP_DISABLED=1. The package
reads only your own memory files in your own VM and sends only
to your own endpoint.
