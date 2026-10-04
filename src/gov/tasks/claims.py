"""The claim lock (CAP-23.a, DEC-292): ``.tickets/.claims/<ticket id>``, created with O_EXCL, naming its holder.

Only the holder releases, and nothing expires. The holder is written as one
line; a reader waits for the end of that line, so a process that loses a race
does not report what it reads between the winner's creation and its write. A
lock file that stays empty is still a held claim, with ``""`` as its holder.
"""

from __future__ import annotations

import fcntl
import os
import time
from pathlib import Path

from gov.cli.errors import GovError
from gov.tasks.tickets import TICKETS_REL, frontmatter

CLAIMS_REL = f"{TICKETS_REL}/.claims"
WRITE_WAIT_S = 2.0  # how long a reader waits for the holder's line


def _is_id(ticket: str) -> bool:
    return bool(ticket) and "/" not in ticket and os.sep not in ticket


def holder(root: Path, ticket: str) -> str | None:
    """The holder of the ticket's claim; None when nobody holds it."""
    if not _is_id(ticket):
        return None
    lock, deadline = Path(root) / CLAIMS_REL / ticket, time.monotonic() + WRITE_WAIT_S
    while True:
        try:
            text = lock.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            return None
        if text.endswith("\n") or time.monotonic() >= deadline:
            return text.strip()
        time.sleep(0.01)


def claim(root: Path, ticket: str, holder_name: str) -> dict:
    """Claim the ticket for ``holder_name``: exactly one claim on a ticket succeeds."""
    front = frontmatter(Path(root) / TICKETS_REL / f"{ticket}.md") if _is_id(ticket) else None
    if front is None:
        raise GovError("TICKET_NOT_FOUND", f"{ticket}: no such ticket", {"ticket": ticket})
    if front.get("status") == "closed":
        raise GovError("TICKET_CLOSED", f"{ticket} is closed and cannot be claimed", {"ticket": ticket})
    lock = Path(root) / CLAIMS_REL / ticket
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        current = holder(root, ticket)
        raise GovError("CLAIM_HELD", f"{ticket} is already claimed by {current}",
                       {"ticket": ticket, "holder": current}) from None
    try:
        os.write(descriptor, f"{holder_name}\n".encode("utf-8"))
    finally:
        os.close(descriptor)
    return {"ticket": ticket, "holder": holder_name}


def release(root: Path, ticket: str, holder_name: str) -> dict:
    """Remove the ticket's lock, for its holder only.

    Reading the holder and removing the lock are one step: both happen under an
    exclusive ``flock`` on the claims folder, which every release takes. Only a
    release removes a lock, so the lock read under it is the lock removed, and
    a release never removes a lock that was created after it read the holder.
    """
    claims, current = Path(root) / CLAIMS_REL, None
    if _is_id(ticket) and claims.is_dir():
        folder = os.open(claims, os.O_RDONLY)
        try:
            fcntl.flock(folder, fcntl.LOCK_EX)
            current = holder(root, ticket)
            if current is not None and current == holder_name:
                (claims / ticket).unlink()
                return {"ticket": ticket, "holder": holder_name}
        finally:
            os.close(folder)  # closing the folder ends the flock
    raise GovError("CLAIM_NOT_HELD", f"{ticket} is not claimed by {holder_name} (holder: {current})",
                   {"ticket": ticket, "holder": current})
