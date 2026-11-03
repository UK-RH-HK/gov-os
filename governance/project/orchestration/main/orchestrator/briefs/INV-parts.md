# The investigation's parts (DEC-1047). Each investigator does exactly one part; reports go to
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/INVESTIGATION-1/<part>.md`.

## A1 — the owner's named practices, 1 to 5 (and every other of their kind you find)
1. The full `gov check` in every lead's verification (where leads run it: `governance/project/briefs/LEAD-w2-common.md`,
   the lead logs; its families and their times; which families a change can affect).
2. Real-model tests (W1-19, W1-21: the real embedder and reranker) in tickets' scoped runs (`select_tests.py`, the
   test map); their time and their failure modes under load.
3. The guard's ~9,000 tests (W1-02 about 3,655, unit/guard about 1,100, W1-47 980, W2-58 808, W2-50 636, W2-84 329,
   W1-04 336: `drafts/INVENTORY-TESTS-CODE-1.md`) in tickets' runs: when the selection pulls them in, their time.
4. `gov context` loading the whole decision register for every cited decision (1,619,286 tokens against a limit of
   6,000, W2-126's lead checkpoint): why, where (`src/gov/context*`, `src/gov/decisions`), what the packet is used for.
5. The ~56,000-character lead briefs (`briefs/*-A5-*.md`, `LEAD-w2-common.md`, `build_lead_brief.py`): what a lead
   needs, what it reads, what it pays per launch.

## A2 — the owner's named practices, 6 to 10 (and every other of their kind you find)
6. The guard-refusal harvest re-scanning every transcript every minute (`tools/guard_refusals.py`, the dispatcher's
   harvest, `dispatch/guard-harvest.json`, its run times in `dispatch/dispatch.log`).
7. Attribution re-running each red three times with and without the batch (`tools/land.py`, `close_build.py`,
   the merge queue under `governance/project/orchestration/tools/`; the landing logs `log/land-dispatch-*.out`).
8. Tests starting their own code-graph daemons (`codebase-memory-mcp --cbm-daemon-internal` processes; which tests,
   how many per run, their CPU).
9. Review effort not matched to risk (FULL / STANDARD / LITE, `--effort max` reviewers, two rounds, probe records:
   `docs/probes/`, the reviews in `.gov-runtime/scratch/orchestrator/reviews/`).
10. The ceremony around small decisions: register entries for P3s, six-part packages, pings, the status block, the
    checkpoints and record syncs, the trailer rules (`docs/DECISION_REGISTER.md` size and growth, packages count,
    `pings.log`).

## B1 — the Gov OS product: gates, checks, close, records
`src/gov/check`, `src/gov/close`, `src/gov/records`, `src/gov/decisions`, `src/gov/checkpoint`, `src/gov/ci`,
`src/gov/doctor`, `src/gov/accept`, `src/gov/release`, `src/gov/pause`, the path map and test map, and the tests that
exist only to build or enforce them. DEC-953's lifted list (`governance/project/orchestration/LIFTED-BY-DEC953.md`)
says what is already lifted here: say whether each lifted gate should also leave the product's defaults, and what else
should be lifted, scoped or kept.

## B2 — the Gov OS product: the guard, the kernel, the Contract's ceremonies
`src/gov/guard` (the five rules DEC-953 kept; what each costs and protects; the code and tests that exist only for
rules already lifted), the hooks (`.claude/hooks/`, `template/governance/kernel/hooks/`), the kernel template
(`template/governance/kernel/`: roles, skills, briefs), the Contract (`docs/contract/`) and the Charter where they
impose ceremony (records, trailers, checkpoints, accepted-history, ratchets), `docs/checkpoints/`, `docs/close/`.

## C — the CTO's own tools and practices
`.gov-runtime/scratch/orchestrator/tools/` (about 12,000 lines), `governance/project/orchestration/` (the dispatcher,
the nightly, the sync, packages, closes, sessions), the orchestrator prompt (`governance/project/prompts/w2-orchestrator.md`,
about 430 lines, 43,000 tokens), `DECISIONS-IN-FORCE.md`, the checkpoint and RESUME HERE, the morning package, the
watchers (sentinel, inbox waiter, dead-man's switch), the drift logs, the approval queue. What each costs the owner,
the CTO's tokens and the machine, and what it protects.

## D — the WBS and the tickets
`docs/plan/WAVE_2_WBS.md`, `docs/plan/WAVE_2_REVISED_PLAN.md`, `docs/plan/WAVE_2_LIST.md`, `.tickets/` (136 in Wave 2:
45 closed). Which tickets, and which KPI lines inside tickets, exist only to build, extend or polish what parts A to C
are likely to recommend lifting (gates, ceremonies, checks, guard read rules beyond the five, records); which are still
needed for the aim's four needs; which can be merged or retired; which are done in substance by the emergency (W2-112,
W2-122, W2-123, W2-126, W2-20's gate lines, the dispatcher and Load Balancer). Feeds DEC-1039 step 3b. Give, per ticket
open or in flight: keep / merge into <id> / retire / re-scope, with its KPI lines' fate.

## E — the fresh-repository question
Copy what works into a separate, fresh repository and start over with less bureaucracy, or keep this repository and do
the lifting and refactoring here? Inventory what works and would be copied (memory: lexical, semantic, rerank, the
vector cache, seeding; the roles and the guard's five rules; the dispatcher and the Load Balancer; the ticket tooling),
what would be left behind (history, the register, records, tests), the cost of each path (days, risks: lost history and
evidence, broken references, re-pinning, the EXAMIN copy's timeline, the record branch, the owner's push), and a
recommendation with its confidence. Read the code's structure (`src/gov/`), the size report
(`drafts/INVENTORY-TESTS-CODE-1.md`), and how coupled the pieces are (imports between `src/gov/*` packages).
