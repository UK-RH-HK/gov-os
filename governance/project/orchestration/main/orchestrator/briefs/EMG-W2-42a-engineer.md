# Emergency task: W2-42a, the guard's parser misreadings fixed in the product (engineer)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** engineer. **Worktree:** `/home/usain/gov-os-worktrees/W2-42a`, branch `w2/W2-42a` (from `w2/integrate` at
`a58ba344`). **Ticket:** `DAEO-03ub` (W2-42a, FULL). TMPDIR `/tmp/gov-os-emg-w242a`. Allowed paths:
`src/gov/guard/decide.py`, `src/gov/guard/reads.py`, `src/gov/guard/bash_writes.py`, `tests/unit/guard/test_w2_42a*`,
`docs/changes/W2-42a-evidence.md`. Nothing else.

## Why (the owner, DEC-1040 item 2, 2026-11-02 ~20:15)
72 of 78 guard refusals since ACT 1 were false; tonight's came mostly from the product's read judge
(`src/gov/guard/reads.py`, `RUNTIME_REFUSAL`, "the call reads files whose names another command gives at run time…"),
which the five-rule hook imports from the pinned judge: python3 and cat heredocs editing a file by its literal path,
a `for i in $(seq 1 16)` wait loop grepping one literal file. The owner: fix the parser's misreadings (heredocs, loops
and substitutions, and the read-listing rule's misreads of literal paths), replayed against every logged refusal and
the planted cases, one review, live with re-pin window 2. **The five rules stay as they are; only the misreadings go.
Never a fail-open:** a write today's parser catches must stay caught; an unknown or unparseable form still refuses.

## The spec
`.tickets/DAEO-03ub.md`: its 11 success lines and 2 failure lines (lines 10 and 11 are new, DEC-1040). **Never read
`tests/acceptance/W2-42a/`** (the test designer writes it in parallel, DEC-820 (c)); you run it once the CTO merges it
(`.gov-runtime/scratch/lead/TESTS-READY` in your tree), results only. The reviewed basis: ACT-GUARD-FIX-3's
`bash_writes.py` and `pretooluse.py`, copies in
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-guard-fix-3/` (its
`ACT-GUARD-FIX-3.md` §7: the eight parser lines). The ticket lets you port `bash_writes.py` as
`src/gov/guard/bash_writes.py`.

## Your own evidence (the ticket's measured line, and the replay for yourself)
The logged refusals are in
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl` (`key` = the
tool-use id; `transcript`; `form` = the first 200 characters only; `verdict`). Recover the full commands from the
transcripts by key with a script, for your own unit tests and the measurement in `docs/changes/W2-42a-evidence.md`:
for every false refusal, which part refused it (the product's read judge, the product's write parser, or the hook's
own `bash_writes.py`), and whether your change now allows it; every true one still refused. **If a false refusal comes
from the hook's own file (a `.claude/` file, the owner's), say so and write the owner's ACT** (the exact change, for
example the hook calling the product's parser); never edit `.claude/`. Secrets: gitleaks any fixture before commit;
never print one.

## Musts
Test-driven unit tests in `tests/unit/guard/test_w2_42a*`; then the scoped set (`select_tests.py`: `src/gov/guard` is
shared core, so the guard's suites W1-02, W1-04, W1-05, W1-33, W1-47, W2-58, W2-50, W2-84 and `tests/unit/guard` will
be selected; all through the gate, one slot at a time) with every red explained against the base; the hook's latency
not worse (`hook_timing.py` in `.gov-runtime/scratch/orchestrator/pin/` or the CTO's tools, if it takes a `src`).
Commits: `Task: DAEO-03ub`, `Implements: DEC-1040,DEC-1028`, `Role: engineer`. Return DONE with the head, the
replay's figures (false allowed now n/N; true still refused n/N), the scoped results, and any ACT for the hook. One
independent review follows (the CTO starts it, effort max), then the merge and re-pin window 2. Estimate: about 600
lines, 3 hours.
