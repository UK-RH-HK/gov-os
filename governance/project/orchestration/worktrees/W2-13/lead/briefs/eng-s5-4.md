# W2-13 engineer, S5: the last line (the CTO)

`src/gov/context/command.py` is now in your paths (merged into your branch by the CTO). Make its `context(...)` call pass `role=getattr(args, "role", None)`, as your evidence names, with a unit test; commit only that file and its test (never `git add -A`: `.claude/hooks/role_reads.py` is stale on disk); update the evidence file. The CTO re-runs `gov accept` outside the sandbox. Return the twelve fields, brief, with the `ps` check.
