"""The context-reproducibility family check (CAP-38.b, W1-24).

Run by ``sh -c`` in the project root (DEC-285). Exit 0 is green: every ticket's
context hash is the same across two computations.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    try:
        from gov.store import connect
        conn = connect(root)
        try:
            tickets = conn.execute(
                "SELECT id FROM records WHERE type = 'ticket'"
            ).fetchall()
        finally:
            conn.close()
    except Exception as exc:
        print(f"context-reproducibility: cannot read the store: {exc}")
        return 1

    if not tickets:
        print("unmeasured: no tickets in the store")
        return 1

    from gov.context import context

    failures = 0
    errors = 0
    for (ticket_id,) in tickets:
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

    if errors == len(tickets):
        print("unmeasured: every ticket's context computation failed")
        return 1

    if failures or errors:
        print(f"context-reproducibility: {failures} ticket(s) failed, {errors} error(s)")
        return 1

    print("context-reproducibility: green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
