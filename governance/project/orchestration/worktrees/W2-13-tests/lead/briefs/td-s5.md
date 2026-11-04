# W2-13 (DAEO-zqvn): independent-test-designer, the DEC-1065 round (D-4b; launched by the CTO, no lead)

Your worktree is `/home/usain/gov-os-worktrees/W2-13-tests`. Read and follow
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md` (the common
rules, its "Test designer" paragraph), with ticket id `DAEO-zqvn`.

**Your KPI line this round:** S5 (search respects role separation, DEC-1065 (2)), as the ticket states it.

Facts for your cases (from the integrated code, read freely): no product code reads `role_paths` today; `--role` is parsed (`src/gov/cli/main.py:130`) and never used; the keyword index holds `tests/**` (`lexical.py:119`), the vectors hold `tests/**` and `src/**`; the guard's matcher is `.claude/hooks/role_reads.py` (`{ticket_tests}`, `{ticket_impl}`; a `class: coordination` ticket's own folder only). Cases: in a planted project with a `role_paths` block and a planted ticket, an engineer's `gov retrieve` (and `gov context`'s supplementary block) returns none of its own ticket's acceptance tests and names what it filtered; a test designer gets none of the ticket's new code in the engineer's tree; other tickets' tests and integrated code still come back; no `role_paths` section: no filter. Use the lexical route only in your planted projects (no embedder: the semantic part reports unavailable, which DEC-1065 (1) wants anyway).
