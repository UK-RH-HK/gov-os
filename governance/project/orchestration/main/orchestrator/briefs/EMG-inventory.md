# Emergency task: the tests and the code inventoried (DEC-1039 item 2, the inventory only)

Read `briefs/EMG-common.md` beside this file first; its rules hold.

**Role:** read-only analyst. You change nothing in the repository: no edit, no commit, no deletion, in any tree. You
write one file: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/INVENTORY-TESTS-CODE-1.md`
(and helper scripts or raw outputs under `/tmp/gov-os-emg-inventory/`). Read the main tree at `w2/integrate`
(`/home/usain/Dynamic-Agentic-Engineering-OS`). Never read `~/gov-os-workbench`.

## The owner's words (DEC-1039 item 2)
"A report of the code's size (files and lines: product code, tests, tools), the number of tests (unit, acceptance),
which are no longer needed, which repeat each other or can be merged, even across tickets. Then test designers refactor
the tests (an independent reviewer checks them) and a senior engineer refactors the code. Every KPI line stays covered
by at least one test; the list of deletions and merges goes to the owner first." The refactor waits; you do the report.

## The report, in this order
1. **Size:** files and lines (code lines without blanks and comments, and total) for: product code (`src/`), unit
   tests (`tests/unit/`), acceptance tests (`tests/acceptance/`, per ticket folder), other tests, the kernel template
   (`template/`), the CTO's tools (`governance/project/orchestration/tools/`, `.gov-runtime/scratch/orchestrator/tools/`,
   `docs/plan/tools/`). A table, with the largest 20 files of each.
2. **The number of tests:** cases per suite (unit by folder; acceptance by ticket), from one `pytest --collect-only -q`
   over `tests` run through the gate (`heavy_slot.sh`, with `PYTHONPATH=<main tree>/src`); and the slowest suites
   from the last nightly's results (`log/nightly/20261102-0400/` under the CTO's scratch: JUnit XML durations).
3. **No longer needed:** tests that enforce a superseded or replaced decision (search the register,
   `docs/DECISION_REGISTER.md`, for "SUPERSEDED", "Replaces", "replaced by"; for example DEC-798's CPU-only cases,
   which a test designer is revising right now in `tests/acceptance/W2-54/`), tests of retired code, and skipped tests
   that can never run here. **Not** the tests of features DEC-953 lifted as gates: they stay built and tested.
4. **Repeats and merges, even across tickets:** cases that check the same behaviour (the same public call with the
   same expectation, the same fixture built in several places, parametrisable families), with each group's files and
   case ids and the saving (cases, lines, seconds from the nightly durations).
5. **KPI coverage kept:** for every proposed deletion or merge, the KPI lines its cases cover (from each acceptance
   folder's README map and the ticket's `covers`), and the test that keeps covering each after the change. A KPI line
   with no other coverage blocks its deletion.
6. **The list for the owner:** one table, deletions and merges, each with its reason, its saving, and its KPI line kept
   by which test; then the code's own candidates for the senior engineer (dead code, duplicated helpers) as a short
   list, with how you found them (static search; name the tool).
Write facts with their evidence (paths, counts, commands). Mark estimates as such.

Return DONE with the report's path and its headline figures (the totals, the number of deletions and merges proposed,
the seconds saved on the nightly). Estimate: 2 hours. Work by searches and scripts, in batches, never one giant query.
