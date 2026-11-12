"""``python3 -m gov.lock``: write the lock of the project in the working directory (the template's Copier task)."""

from __future__ import annotations

import sys
from pathlib import Path

from gov.lock import LockError, write

if __name__ == "__main__":
    try:
        write(Path.cwd())
    except LockError as exc:
        sys.exit(f"gov.lock: framework.lock not written: {exc}")
