"""The planted graphs of W2-147 (S4's list). A wait is a ``waits_on`` entry; every ticket writes a path of its own,
so no ``WRITES_OVERLAP`` or ``NEEDS_WHAT_WRITES`` joins the cycles. Priority 0 sorts first (the fixed key)."""

from __future__ import annotations

from w2_147_support import T

# S1: A and B wait on each other; C, outside the cycle, waits on A and sorts first by the key.
S1 = (
    T("TK-a", "W9-101", waits=("TK-b",)),
    T("TK-b", "W9-102", waits=("TK-a",)),
    T("TK-c", "W9-103", priority=0, waits=("TK-a",)),
)

# S2: the case seen on 2026-11-09, with stand-in tickets of the same shape: W2-145 and W2-137 in a cycle, W2-88
# waiting on W2-145, W2-27 waiting on W2-88; one priority, so WBS order puts W2-27 first. Waits by WBS id with a
# reason, as the ticket store writes them.
S2 = (
    T("DAEO-s145", "W2-145", waits=("W2-137 — the stand-in's wait",)),
    T("DAEO-s137", "W2-137", waits=("W2-145 — the stand-in's wait",)),
    T("DAEO-s088", "W2-88", waits=("W2-145 — needs its tool",)),
    T("DAEO-s027", "W2-27", waits=("W2-88 — needs its result",)),
)

# Two separate cycles (A-B and D-E), a wait between them (E on B), a cycle ticket waiting on an outside ticket
# (A on G), and an outside ticket waiting on the second cycle (F on D) that sorts first by the key. E, the second
# cycle's first ticket by the key, sorts before A too: breaking every wait of the first ticket of any cycle would
# break E's wait on B (between the cycles); only E's wait on D is broken.
TWO_CYCLES = (
    T("TK-g", "W9-201"),
    T("TK-a", "W9-202", waits=("TK-b", "TK-g")),
    T("TK-b", "W9-203", waits=("TK-a",)),
    T("TK-d", "W9-204", waits=("TK-e",)),
    T("TK-e", "W9-205", priority=0, waits=("TK-d", "TK-b")),
    T("TK-f", "W9-200", priority=0, waits=("TK-d",)),
)

# A self-loop: X waits on itself; Y, outside, waits on X and sorts first; Z waits on nothing.
SELF_LOOP = (
    T("TK-x", "W9-301", waits=("TK-x",)),
    T("TK-y", "W9-302", priority=0, waits=("TK-x",)),
    T("TK-z", "W9-303"),
)

CYCLE_GRAPHS = {"s1-outside-waiter": S1, "s2-2026-11-09": S2, "two-cycles": TWO_CYCLES, "self-loop": SELF_LOOP}

# No cycle. S1's tickets without B's wait on A; S2's without W2-137's wait on W2-145.
S1_NO_CYCLE = (
    T("TK-a", "W9-101", waits=("TK-b",)),
    T("TK-b", "W9-102"),
    T("TK-c", "W9-103", priority=0, waits=("TK-a",)),
)
S2_NO_CYCLE = (
    T("DAEO-s145", "W2-145", waits=("W2-137 — the stand-in's wait",)),
    T("DAEO-s137", "W2-137"),
    T("DAEO-s088", "W2-88", waits=("W2-145 — needs its tool",)),
    T("DAEO-s027", "W2-27", waits=("W2-88 — needs its result",)),
)

# No cycle, every other part of the plan: a depends_on, a needs on another's writes, two overlapping writes, a reads
# overlap (READS_WIDE), an override, a closed ticket, a wait on an open record (held, and a ticket held with it),
# an unknown wait (a finding, exit 1), no needs: (a finding) and an in-progress ticket.
MIXED_NO_CYCLE = (
    T("MX-01", "W9-401", status="in_progress", extra={"allowed_paths": ["src/lib/core.py"]}),
    T("MX-02", "W9-402", extra={"allowed_paths": ["src/app/**"], "needs": ["src/lib/core.py"]}),
    T("MX-03", "W9-403", extra={"allowed_paths": ["src/w/**"]}),
    T("MX-04", "W9-404", priority=3, extra={"allowed_paths": ["src/w/x.py"]}),
    T("MX-05", "W9-405", extra={"depends_on": ["MX-03"], "deps": ["MX-03"]}),
    T("MX-06", "W9-406", extra={"allowed_paths": ["docs/f.md"], "reads": ["src/**"]}),
    T("MX-07", "W9-407", extra={"allowed_paths": ["src/g/**"], "needs": None}),
    T("MX-08", "W9-408", extra={"allowed_paths": ["src/w/y.py"], "plan_override": "DEC-899"}),
    T("MX-09", "W9-409", status="closed"),
    T("MX-10", "W9-410", waits=("docs/rec.md — the open record",)),
    T("MX-11", "W9-411", waits=("MX-10",)),
    T("MX-12", "W9-412", waits=("NOPE-1 — names nothing",)),
    T("MX-13", "W9-413", priority=0, waits=("MX-02", "W9-405")),
)
MIXED_FILES = {"docs/rec.md": "---\nstatus: open\n---\n# an open record\n"}

NO_CYCLE_GRAPHS = {"s1-without-the-cycle": (S1_NO_CYCLE, {}), "s2-without-the-cycle": (S2_NO_CYCLE, {}),
                   "mixed": (MIXED_NO_CYCLE, MIXED_FILES)}
