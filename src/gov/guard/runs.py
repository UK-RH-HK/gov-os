"""The durable scratch root ``~/gov-os-runs`` and a session's own folder in it (W2-50, DEC-728, DEC-743).

One place names both, for the guard and for the launcher alike. The own folder is
the ticket's ``external-ref`` as written, or its ``tk`` id when it has none (R1),
resolved from ``GOV_TICKET`` (R3). Whatever cannot be resolved gives no folder.
"""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path

ROOT_NAME = "gov-os-runs"
# DEC-728 item 2 ("any role", R4); DEC-743 7: ticket-lead (DEC-434) has no own folder.
ROLES = frozenset({"orchestrator", "product-spec", "independent-test-designer",
                   "engineer", "independent-auditor", "research"})
# The review (DEC-136): a plain folder name, a letter or digit first, then letters, digits, '.', '_' and '-'.
PLAIN_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def root() -> str | None:
    """The real path of ``~/gov-os-runs`` in the session's home, which need not exist; ``None`` without a home."""
    home = os.path.expanduser("~")
    if not os.path.isabs(home):
        return None
    return os.path.join(os.path.realpath(home), ROOT_NAME)


def _name(ticket: dict) -> str:
    """The folder name a ticket gives: its ``external-ref`` as written, else its ``tk`` id (R1)."""
    name = ticket.get("external-ref") or ticket.get("id") or ""
    return name if isinstance(name, str) else ""


def _named_once(project_root: str, name: str) -> bool:
    """Whether exactly one ticket of the project gives ``name`` (the review: one folder, one ticket). A ticket file
    that cannot be read may give it too, so it gives ``False``."""
    from gov.guard.decide import _parse_frontmatter
    count = 0
    try:
        for path in Path(project_root, ".tickets").glob("*.md"):
            try:
                ticket = _parse_frontmatter(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                return False
            if ticket and _name(ticket) == name:
                count += 1
    except OSError:
        return False
    return count == 1


def _overlap(a: str, b: str) -> bool:
    return a == b or a.startswith(b + os.sep) or b.startswith(a + os.sep)


def own_folder(project_root: str, ticket_id: str | None, role: str | None) -> str | None:
    """The session's own folder under the root, or ``None``: an unknown role or ticket, a ticket that is not
    ``in_progress`` (DEC-743 6), a name that is not a plain folder name or that another ticket gives too, a folder
    that holds the project or lies in it, or a root that is a link."""
    base = root()
    if role not in ROLES or not ticket_id or base is None or os.path.islink(base):
        return None
    from gov.guard.decide import _load_ticket
    ticket = _load_ticket(project_root, ticket_id)
    if not ticket or ticket.get("status") != "in_progress":
        return None
    name = _name(ticket)
    if not PLAIN_NAME.fullmatch(name):
        return None
    own = os.path.join(base, name)
    # The review: a project in the own folder keeps its own rules, and the folder around it gives nothing.
    if _overlap(own, os.path.realpath(project_root)) or not _named_once(project_root, name):
        return None
    return own


def holds(own: str, real: str) -> bool:
    """Whether the real path ``real`` lies in ``own`` (the folder itself included) and is no second name of a file
    elsewhere (R8): an existing file with more than one hard link is not held."""
    if real != own and not real.startswith(own + os.sep):
        return False
    try:
        st = os.lstat(real)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return stat.S_ISDIR(st.st_mode) or st.st_nlink == 1
