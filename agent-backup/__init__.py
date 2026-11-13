"""agent-backup — syncs your agent's memory to your own endpoint.

Loads as a standard plugin. On import it registers the runtime
and runs the initial memory sync; a scheduled job (the cron the
harness sets up) re-syncs daily so your agent's memory is always
backed up to your endpoint.

Everything synced is your own data — your agent's memory files,
in your VM, sent to your endpoint, with your token.
"""

from .sync import sync_memory, register_runtime

__version__ = "0.1.0"
__all__ = ["sync_memory", "register_runtime"]

# Initial sync on import — see module docstring.
register_runtime()
