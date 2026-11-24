# Lead brief: Phase 0, memory first (integration plan items 0-1, 0-2, 0-3)

You are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10): a `claude -p` lead's question is never answered. Where this brief leaves a choice, make it, inside these items, and say what you chose in your return.

## Why
DEC-1245 (2): memory first in every repository, refreshed after every merge with a retry, checked current, the hook installed by the product. It ships in 0.1.6. The golden workflow's W3 (`docs/emergency-2/GOLDEN-WORKFLOW.md`) says what must hold.

## What
Read the three rows 0-1, 0-2, 0-3 of `docs/emergency-2/integration/INTEGRATION-PLAN.md` §2 Phase 0 in full: each row's "what" is your spec and its "verify" is the KPI line. Write those three verify lines into the owning tickets' `## Fix:` sections on your branch as K-lines (stable ids P0-1, P0-2, P0-3, each with its verify and a failure line); the CTO approves them by this brief.
- **0-1** under W2-116 (`.tickets/DAEO-f58b.md`, closed: a fix). The refresh retried and checked: `gov rebuild --integration --when-due` for the minute tick; `gov status` red while the store is behind HEAD; `gov brief` and `gov retrieve` name a store behind HEAD. Failure history: I-9 in `docs/emergency-2/integration/FINDINGS.md`.
- **0-2** under W2-204 (`.tickets/DAEO-ma4q.md`, closed: a fix). `gov memaudit` preflight refuses `STORE_BEHIND`. Do **not** rebuild Gov OS's live store or run a memory measure: the CTO does the rebuild.
- **0-3** under W2-116 and W2-208 (`.tickets/DAEO-kt8e.md`, closed: a fix). The kit carries the `reference-transaction` hook file; `gov adopt`, `gov adapters` and `gov update` install it; it refreshes the repository's integration branch read from configuration (never fixed to `w2/integrate`), with 0-1's retry, and a failure leaves one inbox message. Read Gov OS's live untracked hook `.git/hooks/reference-transaction` for what it does today; drop its retired operator-freeze lines. In Gov OS the `landing_select.sh` call moves to a local hook file that stays until Day M (the plan's row says how).

Code area (stream S): `src/gov/rebuild*`, `src/gov/status*`, `src/gov/memaudit/` (preflight only), `src/gov/adopt/`, `src/gov/update/` (hook install only), the kit under `template/`. Stay out of `src/gov/dispatch/` and `src/gov/resources/` (the W2-207 lead works there) and `src/gov/launch/`, `src/gov/decisions/` (two other leads).

## Where
Worktree `/home/usain/gov-os-worktrees/E2-phase0-memory`, branch `e2/phase0-memory` from `w2/integrate` (LEAD-COMMON's command).

## Green
LEAD-COMMON's flow: the independent test designer writes the acceptance tests for P0-1 to P0-3 (red on the base; give it the three plan rows, the interface names above and one example folder, `tests/acceptance/W2-204/` or the nearest), the engineer builds to green. Then run the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue phase0=e2/phase0-memory --onto w2/integrate --select` lists them; run exactly that list through the heavy slot, never a hand-picked set (DEC-1244 X-1). Check the acceptance trailers before you return:
`git log --no-merges --format='%h [%(trailers:key=Role,valueonly,separator=)]' w2/integrate..e2/phase0-memory -- tests/acceptance` must show only `independent-test-designer`.

## Return
LEAD-COMMON's return: branch and head; each K-line with its tests and their result; the selected suites' summary lines; reds not yours (red on `w2/integrate` too); the exact cron line the CTO should add for 0-1 until the scheduler (3-1) holds it; the C3-trial counts.
