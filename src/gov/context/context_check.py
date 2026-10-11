"""The context-reproducibility family check (CAP-38.b, W1-24).

Run by ``sh -c`` in the project root (DEC-285). Exit 0 is green: every ticket's
context hash is the same across two computations.

The tickets measured are the project's own: the records of its ticket folder,
whatever name their type has, and no other record of the store (DEC-628). A
file of the folder that the store does not hold as a record is named and the
check is not green: no ticket leaves the measurement unseen.
"""

from __future__ import annotations

import sys
from pathlib import Path

TICKETS_REL = ".tickets"


def project_tickets(root: Path) -> tuple[list, list]:
    """``(ids, unheld)``: the ids of the store's records of the ticket folder, and the files of the folder
    (relative paths) that the store holds no record of."""
    from gov.store import connect
    conn = connect(root)
    try:
        rows = conn.execute("SELECT id, path FROM records").fetchall()
    finally:
        conn.close()
    held = {path: record_id for record_id, path in rows if str(path).startswith(f"{TICKETS_REL}/")}
    folder = Path(root) / TICKETS_REL
    on_disk = sorted(p.relative_to(root).as_posix() for p in folder.rglob("*.md")) if folder.is_dir() else []
    return sorted(set(held.values())), [rel for rel in on_disk if rel not in held]


def main() -> int:
    root = Path.cwd()
    try:
        tickets, unheld = project_tickets(root)
    except Exception as exc:
        print(f"context-reproducibility: cannot read the store or the ticket folder: {exc}")
        return 1

    if not tickets and not unheld:
        print("unmeasured: no tickets of the project in the store")
        return 1

    from gov.context import context

    failures = 0
    errors = 0
    for rel in unheld:
        print(f"ERROR: {Path(rel).stem}: {rel} is a file of the ticket folder that the store holds no record of "
              f"(it cannot be read as a ticket, or the store was loaded before it); not measured")
        errors += 1
    for ticket_id in tickets:
        try:
            h1 = context(root, ticket_id)["hash"]
            h2 = context(root, ticket_id)["hash"]
        except Exception as exc:
            print(f"ERROR: {ticket_id}: {exc}")
            errors += 1
            continue
        if h1 != h2:
            print(f"FAIL: {ticket_id}: {h1} != {h2}")
            failures += 1

    if errors == len(tickets) + len(unheld):
        print("unmeasured: every ticket's context computation failed")
        return 1

    if failures or errors:
        print(f"context-reproducibility: {failures} ticket(s) failed, {errors} error(s)")
        return 1

    print("context-reproducibility: green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
