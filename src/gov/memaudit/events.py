"""The audit's ledger, appended under one lock (Interface item 3; S8, F3).

``ledger.append`` (W2-170) is imported and never copied. Every append here takes one advisory lock on
``runs/<A>/.ledger.lock`` first, so four reader workers and the wrapper process never interleave a line and a ``seq``
is never given twice. Events carry numbers, ids and codes only (F1).
"""

from __future__ import annotations

import fcntl
import os
from pathlib import Path

from gov.memaudit import ledger

LOCK = ".ledger.lock"


def append(run, event: str, **fields) -> dict:
    """One event of the run's ledger, under the lock; the object written."""
    run = Path(run)
    fd = os.open(run / LOCK, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return ledger.append(run, event, **fields)
    finally:
        os.close(fd)  # closing the descriptor releases the lock


def search(run, phase: str, attempt, call, qid, rc: int, ms: int, ok: bool) -> dict:
    """A ``search`` event: ``phase`` is ready, control, attempt, later or pool; ``call`` the kept number or None;
    ``qid`` only for a later search."""
    return append(run, "search", phase=phase, attempt=attempt, call=call, qid=qid, rc=rc, ms=ms, ok=ok)


def spent(run) -> float:
    """The run's spend so far: the sum of the ledger's ``spend`` events."""
    return sum(float(e.get("usd") or 0) for e in ledger.read(run) if e.get("event") == "spend")
