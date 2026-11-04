# W2-13 engineer, S5: one red (the CTO)

The CTO ran `gov accept W2-13` outside the sandbox on `78bf6b34`: 67 passed, 1 failed, every line passes but S5 (11 of
12). The red is `test_engineer_context_supplementary_holds_none_of_its_own_tickets_acceptance_tests[flag]`: with the role
given by the flag (`gov context ... --role engineer`) instead of `GOV_ROLE`, the supplementary block still holds the
engineer's own acceptance tests, because `gov context` passes no role to it. S5 names "GOV_ROLE or --role". The CTO added
`src/gov/context/__init__.py` to your paths (`95fadf90`) and merged it into your branch (`3cccd91f`): pass the parsed
`--role` (as for `gov retrieve`: it may add a filter, never lift the session's) through to the supplementary filter, with a
unit test. Do not merge yourself; do not commit `.claude/hooks/role_reads.py` (its working copy is stale on disk: commit
only the paths you change, never `git add -A`). Run your unit tests; the CTO re-runs `gov accept` outside the sandbox
(inside it the code index is unavailable). Update the evidence file; commit; return the twelve fields with the `ps` check.
