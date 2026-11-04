# W2-13 engineer, S5: one ride-along fix (the CTO; review S5-F1, P2 under DEC-802)

S5's review is READY (`reviews/w2-13.md`, section "S5 (DEC-1065)"). One finding rides along while W2-13 is open:
**S5-F1:** `gov context <ticket> --role engineer` filters by the caller's `GOV_TICKET`, not by the packet's own ticket, so a
packet built from another ticket's session (the CTO's, under W2-00) for an engineer of `<ticket>` withholds none of
`<ticket>`'s tests; with no `GOV_TICKET` it filters nothing. Fix it so `gov context` judges **the packet's own ticket as well
as `GOV_TICKET`** (the union: it can only add to the filter, never lift one), with a unit test showing both: the CTO's
session building an engineer's packet for another ticket withholds that ticket's tests, and a lead's own case is unchanged.
About 5 lines, in your paths (`src/gov/context/__init__.py`, `src/gov/retrieval/supplementary.py`,
`src/gov/guard/role_paths.py`). Same rules as before; commit only your files (never `git add -A`: `.claude/hooks/role_reads.py`
is stale on disk); update the evidence file. Return the twelve fields, brief, with the `ps` check.
