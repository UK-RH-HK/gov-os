# Lead brief: fix the fresh 80's writer loop (I-23 with EF-9, I-18, I-19; fixes under W2-204)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10). Use the `systematic-debugging` skill before changing code.

## Why
EXAMIN's memory measure (the owner's priority, DEC-1232 (1) item 4) is blocked: on 0.1.5, 5 of 11 halves written today were refused at pre-flight 1, a pair was lost at the final pre-flight, and three clean re-rolls were each refused on a different code. Read rows I-18, I-19 and I-23 of `docs/emergency-2/integration/FINDINGS.md`. The EXAMIN CTO's reading of the code (EF-9): `gov memaudit deliver` checks only file names and counts (`deliver.py` `_writer`), never the per-question checks pre-flight will refuse (`form_ok`, PF-IDEXISTS, PF-DRAWN and the other per-question codes), and the writer has no shell, so it cannot see a fault before the code refuses it; and the round-2 writer brief carries only the checker notes, never the pre-flight-1 refusals (I-23). Verify both in the code before you fix them.

## What (KPI lines, written into `.tickets/DAEO-ma4q.md` (W2-204, closed) as `## Fix:` sections on your branch; the CTO approves them by this brief)
- **FM-1 Deliver refuses what pre-flight would refuse, with codes only.** `gov memaudit deliver` runs every per-question pre-flight check (the set-level ones too where a half is complete) on the writer's files before accepting them, and refuses with the codes and question ids only (never the question text or gold, so nothing leaks to a reader), so the same writer round can be relaunched to repair them. Reuse pre-flight's own check functions; do not copy them. A half that passes deliver passes pre-flight 1 on the same files.
- **FM-2 Round 2 sees pre-flight 1's refusals (I-23).** When pre-flight 1 refuses questions, the round-2 writer brief and the round-2 checker brief carry each refused id with its code (codes and ids only), and the round-2 writer is told to repair or replace exactly those.
- **FM-3 A void is said at once (I-18).** The void count runs as soon as the last checker notes land, and a half that cannot keep the minimum is declared void then, with the counts, not at a later step.
- **FM-4 A stop names its cause (I-19).** Every stop of `gov memaudit fresh` prints its code and reason; no bare `UsageError`.

Keep the hidden-set protections unchanged (EMERGENCY-2 §2.7): nothing you add prints or logs a hidden question's text, gold or sources outside the tool.

Code area: `src/gov/memaudit/` (`deliver.py`, the brief writer, `fresh.py`); call `preflight.py`'s check functions and change that file only if a function must be made importable (another lead adds a `STORE_BEHIND` check there: keep your edits to it minimal). Stay out of every other package.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-fix-memaudit`, branch `e2/fix-memaudit` from `w2/integrate`.

## Green
The test designer writes acceptance tests for FM-1 to FM-4 (red on the base) with planted sets only, never a real evaluation set (no file under `fixtures/evaluation/` is read); the engineer builds. Then exactly the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-ma4q=e2/fix-memaudit --onto w2/integrate --select`, through the heavy slot (DEC-1244 X-1); `gov accept` through the heavy slot too. Errors in `tests/acceptance/W1-35/` or `tests/unit/dispatch/` when run together are I-22, not yours. Check the acceptance trailers (LEAD-COMMON).

## Return
Branch and head; the cause of each finding confirmed in the code (file:line); FM-1 to FM-4 with tests and result; the selected suites' summary lines; reds not yours; the C3-trial counts. The CTO cuts a patch release with it, so say plainly if anything is not finished.
