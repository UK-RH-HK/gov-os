"""The close's serial phase and the routes of the serial-only list (W2-57; DEC-889 item 5, DEC-925 item 3).

The list is the plugin's (``gov_close_serial_only.LIST_REL``): an entry is the text before `` #``, and in this
project the comment that follows is ``<route>: <kind>: <reason>``. The route is the comment's first word, before
its first ``:``:

- ``serial``: the entry is kept in the close, left out of its parallel run and run afterwards, alone and serially;
- ``nightly``: the entry is routed to the nightly, collected by the close and left out of both its phases (the
  plugin deselects every listed entry from the parallel run, whatever its route).

Nothing is routed out of the close by default (fail closed): an entry whose route cannot be read (no comment, an
unknown first word) stays in the serial phase, and so does an entry that a second line of the list keeps there.
"""

from __future__ import annotations

from pathlib import Path

from gov.close.pytest_plugin import gov_close_serial_only as serial_only

NIGHTLY = "nightly"


def nightly(root: Path) -> set[str]:
    """The entries of the project's list that every line naming them routes to the nightly; none without a list.

    A list that is not UTF-8 text raises ``UnicodeDecodeError``, as ``gov_close_serial_only.entries`` does: it is
    never read as "no list" (DEC-555)."""
    path = Path(root) / serial_only.LIST_REL
    if not path.is_file():
        return set()
    routed, kept = set(), set()
    for line in path.read_text(encoding="utf-8").splitlines():
        entry, _, comment = (" " + line).partition(" #")
        entry = entry.strip()
        if entry:
            (routed if comment.split(":")[0].strip() == NIGHTLY else kept).add(entry)
    return routed - kept


def phase(root: Path, declared: list[str]) -> list[str]:
    """The entries of ``declared`` the close's serial phase runs, in their order: every one the list does not route
    to the nightly."""
    routed = nightly(root)
    return [entry for entry in declared if entry not in routed]
