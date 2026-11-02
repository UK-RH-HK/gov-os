"""The context-reproducibility family check (CAP-38.b, W1-24).

Run by ``sh -c`` in the project root (DEC-285). Exit 0 is green: every ticket's
context hash is the same across two computations.

The tickets measured are the project's own: the records of its ticket folder,
whatever name their type has, and no other record of the store (DEC-628). A
file of the folder that the store does not hold as a record is named and the
check is not green: no ticket leaves the measurement unseen. A file whose name
does not end in ``.md`` and two files that carry one id are named too (W2-M228,
W2-L219). A store built from another commit than ``HEAD`` is not measured: the
check says so and is not green, so it never gives a stale store's result for
the tree's (W2-M294).
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
    on_disk = sorted(p.relative_to(root).as_posix() for p in folder.rglob("*") if p.is_file()) \
        if folder.is_dir() else []
    return sorted(set(held.values())), [rel for rel in on_disk if rel not in held]


def stale_store(root: Path) -> str | None:
    """Why the store is not the one of ``HEAD``, or None where it was built from ``HEAD``.

    ``HEAD`` is read through the store loader's own git call (W2-05's sweep, row 41: ``git_env(root, pinned=True)``),
    the call that wrote the commit the store states; this file starts no git of its own (AR-2). A ``HEAD`` that
    cannot be read is a reason, never a pass."""
    from gov.cli.errors import GovError
    from gov.store import connect
    from gov.store.loader import _git, fingerprints
    try:
        head = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("utf-8", "replace").strip()
    except GovError:
        return "the commit HEAD cannot be read"
    if not head:
        return "the commit HEAD cannot be read"
    conn = connect(root)
    try:
        row = fingerprints(conn)
    finally:
        conn.close()
    if row is None or not row.get("head"):
        return "the store states no commit it was built from"
    if row["head"] != head:
        return f"the store was built from {row['head'][:12]}, not from HEAD {head[:12]}"
    return None


def duplicate_ids(root: Path) -> dict:
    """id -> the ticket files (relative paths) that carry it, where more than one does."""
    from gov.tasks.tickets import frontmatter
    folder = Path(root) / TICKETS_REL
    carried: dict[str, list] = {}
    for path in sorted(folder.rglob("*")) if folder.is_dir() else []:
        front = frontmatter(path) if path.is_file() else None
        if front and front.get("id"):
            carried.setdefault(str(front["id"]), []).append(path.relative_to(root).as_posix())
    return {rid: paths for rid, paths in sorted(carried.items()) if len(paths) > 1}


def main() -> int:
    root = Path.cwd()
    try:
        tickets, unheld = project_tickets(root)
        stale = stale_store(root)
        twice = duplicate_ids(root)
    except Exception as exc:
        print(f"context-reproducibility: cannot read the store or the ticket folder: {exc}")
        return 1

    if not tickets and not unheld:
        print("unmeasured: no tickets of the project in the store")
        return 1
    if stale:
        print(f"unmeasured: stale store: {stale}; rebuild it from HEAD before the context is measured")
        return 1

    from gov.context import context

    failures = 0
    errors = 0
    for rid, paths in twice.items():
        print(f"ERROR: {rid}: duplicate id: the ticket files {', '.join(paths)} carry it; not measured as one ticket")
        errors += 1
    for rel in unheld:
        why = "its name does not end in .md" if not rel.endswith(".md") else \
            "it cannot be read as a ticket, or the store was loaded before it"
        print(f"ERROR: {Path(rel).stem}: {rel} is a file of the ticket folder that the store holds no record of "
              f"({why}); not measured")
        errors += 1
    measured = refused = 0
    for ticket_id in tickets:
        try:
            h1, h2 = (_outcome(context, root, ticket_id) for _ in range(2))
        except Exception as exc:
            print(f"ERROR: {ticket_id}: {exc}")
            errors += 1
            continue
        measured += 1
        if h1 != h2:
            print(f"FAIL: {ticket_id}: {h1} != {h2}")
            failures += 1
        elif not isinstance(h1, str):  # the same refusal twice: the context's answer, reproduced (W2-04)
            print(f"REFUSED: {ticket_id}: {h1[1]} tokens of its own text and mandatory inputs, over the ceiling "
                  f"of {h1[2]}")
            refused += 1

    if not tickets:
        print(f"unmeasured: the ticket folder holds only files the store holds no record of ({len(unheld)} named "
              f"above); no ticket's context was computed")
        return 1
    if not measured:
        print("unmeasured: every ticket's context computation failed")
        return 1

    if failures or errors:
        print(f"context-reproducibility: {failures} ticket(s) failed, {errors} error(s)")
        return 1

    print(f"context-reproducibility: green ({measured - refused} packet(s) built twice alike, {refused} refused "
          f"over the ceiling twice alike)")
    return 0


def _outcome(context, root: Path, ticket_id: str):
    """The packet's hash, or the refusal over the ceiling as ``(code, mandatory tokens, ceiling)``; any other error
    is raised."""
    from gov.cli.errors import GovError
    from gov.context import OVER_CEILING
    try:
        return context(root, ticket_id)["hash"]
    except GovError as exc:
        if exc.code != OVER_CEILING:
            raise
        return exc.code, exc.details["mandatory_tokens"], exc.details["limit"]


if __name__ == "__main__":
    sys.exit(main())
