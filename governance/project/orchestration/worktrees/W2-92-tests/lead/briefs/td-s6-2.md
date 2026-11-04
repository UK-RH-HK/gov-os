# W2-92 test designer, S6 round 2 (the CTO)

Same rules as before (stand-ins only; no `gov retrieve` in the sandbox; the `ps` check; do not merge: the CTO merges
outside the sandbox). The CTO ran `gov accept W2-92` outside the sandbox at the engineer's head (`4e9ba434`): 44 passed,
1 failed: `test_s6b_a_title_is_the_one_the_store_was_built_with`. **The CTO's decision (P2, under DEC-342):** the case's
premise is wrong, not the code. After `_retitled` edits the working file, the lexical index is stale, and under DEC-342 a
stale index cites no chunk at all (`retrieve.py:156`), whatever the title's source; so the bundle is empty for that reason,
and the case's message ("the title was read from the working tree's file") misattributes it. The engineer reproduced it:
with the lexical index refreshed after the edit (change uncommitted), the record comes back by the store's title. Revise
s6b so it tests what S6 says: either refresh the lexical index after the edit (so freshness is not the cause), or judge the
record route's own start ids (the record found by the store's title, and not by the new title) instead of the bundle's
text; keep its intent (the edit is not read for the title) and keep a case that still fails on code that reads the working
file's title (plant it in a scratch copy, never committed). Commit only `tests/acceptance/W2-92/**` with `Task: DAEO-n0wb`,
`Implements: DEC-1065`, `Role: independent-test-designer`, `Rewrite-Reason: s6b's premise (a stale index cites nothing,
DEC-342)`, Co-Authored-By. Return the twelve fields, brief, with the commit.
