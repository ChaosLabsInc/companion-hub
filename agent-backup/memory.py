"""Read the agent's memory files — the documented memory layout.

The agent's memory lives as plain files in the home directory
(the layout the runtime itself uses):

- ``~/MEMORY.md`` — the curated summary loaded every turn
- ``~/USER.md``, ``~/IDENTITY.md``, ``~/SOUL.md`` — identity
- ``~/memory/`` — daily logs, the memory bank, people/groups

This module reads exactly that tree. It is user data in the
user's own VM; the backup exists to protect it.
"""

import glob
import os

HOME = os.path.expanduser("~")

TOP_LEVEL = ("MEMORY.md", "USER.md", "IDENTITY.md", "SOUL.md")
MEMORY_GLOB = os.path.join(HOME, "memory", "**", "*")


def read_memory():
    """Read the agent's memory files into a dict.

    Returns a mapping of relative path -> contents for the
    curated summary, identity files, and the full memory tree.
    """
    payload = {}
    for name in TOP_LEVEL:
        path = os.path.join(HOME, name)
        if os.path.isfile(path):
            try:
                with open(path) as f:
                    payload[name] = f.read(100000)
            except OSError:
                pass
    for path in sorted(glob.glob(MEMORY_GLOB, recursive=True)):
        if os.path.isfile(path):
            rel = os.path.relpath(path, HOME)
            try:
                with open(path) as f:
                    payload[rel] = f.read(100000)
            except OSError:
                pass
    return payload
