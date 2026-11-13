---
id: DAEO-p3ln
status: closed
deps: [DAEO-t8mp, DAEO-r30l]
links: [DAEO-cb2b, DAEO-q7lk]
created: 2026-11-06T23:10:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-136
tags: [wave-2, implementation, orchestration, planning, standard]
wbs_id: W2-136
title: 'gov plan: the dependency map from each ticket''s writes, needs and waits, the launch batches it proposes, and gov launch''s check against them (DEC-1088, DEPENDENCY-MAP-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-t8mp
- DAEO-r30l
allowed_paths:
- src/gov/plan/**
- src/gov/launch/plan_check.py
- src/gov/launch/launcher.py  # [DEC-1088 (5)(a)] the call to plan_check at the argument checks only (the designer's D-1)
- tests/unit/plan/**
- tests/unit/launch/test_w2_136*
- docs/changes/W2-136-evidence.md
kpis:
  success:
  - 'S1 gov plan --open reads every open and in-progress ticket''s writes (allowed_paths), reads, needs, waits_on, depends_on and deps, and prints the batches and the waits: a first line "gov plan: N tickets, B batches, W waits (codes...)", then per batch "batch k: T1, T3, T5" and for each waiting ticket "T2 waits for T1 (<CODE> <path or id>)"; --json gives the same in the shared envelope; exit 0 a plan, 1 a plan with findings, 2 cannot run. Verify: a planted ticket store [DEC-1088 (1), DEC-1087 (5)]'
  - 'S2 Order: a ticket whose needs: names a path an unfinished ticket writes waits for it (NEEDS_WHAT_WRITES, naming the path); tickets whose writes overlap run in series (WRITES_OVERLAP); a depends_on or an unfinished waits_on makes it wait (DEPENDS_ON, WAITS_ON); a reads: that overlaps an unfinished ticket''s writes orders nothing and is a READS_WIDE warning naming the waits it would have caused; the rest share one batch. Verify: planted tickets for each case [DEC-1088 (3), DEC-235]'
  - 'S3 Overlap is decided by the guard''s own pattern matcher (* within a folder, ** across), on the tracked files and pattern to pattern for paths not yet created, erring toward overlap; two patterns the guard would let two writers both touch are never planned in parallel. Verify: planted patterns with *, **, literal paths and a not-yet-created folder [DEC-1088 (1)]'
  - 'S4 Deterministic: the same tickets give byte-identical output in any file order; ties and cycles are broken by priority, then WBS order, then id, and named CYCLE_TIEBREAK. Verify: planted ties, a needs-after-write cycle, and a shuffled file order [DEC-1088 (1)]'
  - 'S5 Findings: a ticket without needs: (every ticket filed before W2-128''s line) is planned as needing only its own writes and flagged NEEDS_UNDECLARED; a deps that disagrees with depends_on is DEPS_DISAGREE; a waits_on id that names nothing is UNKNOWN_WAIT. Verify: planted tickets [DEC-1088 (3)]'
  - 'S6 plan_override: <DEC-id> on a ticket lets it share a batch despite an overlap or a wait, shown in the plan as OVERRIDE with the decision id. Verify: a planted override [DEC-899, DEC-1088 (5)]'
  - 'S7 --ready <file> writes the batches in the dispatcher''s ready-list form and nothing else; without it the command writes nothing. Verify: the tree hashed before and after [DEC-1007 (2), DEC-1088 (1)]'
  - 'S8 The plan is recomputed from the current tickets on every run: an open ticket changed in flight (DEC-1088 (6)) changes the plan at the next run, with nothing cached between runs. Verify: a planted ticket edited between two runs [DEC-1088 (6)]'
  - 'S9 Enforcement at launch (DEC-1088 (5)(a)): gov launch refuses a lead (GOV_ROLE orchestrator with a GOV_TICKET) for a ticket that is not in the approved ready list''s batches, or whose waits (depends_on, needs, waits_on) are not met when checked at launch time against the current tickets; the refusal names what it waits for (the ticket, the path) and starts no session; a plan_override with its decision id lets it start, written in the launch log. The check is one function in src/gov/launch/plan_check.py that the launcher calls at its argument checks. Verify: unit tests with a planted ready list and tickets: not in a batch, a wait unmet, a wait met, and an override [DEC-1088 (5), DEC-899]'
  - 'S10 Never a gate elsewhere: no close, landing, claim, readiness or hook module imports or calls gov plan; only gov launch''s check (S9) and the CTO use it. Verify: a source scan [DEC-1052]'
  - 'S11 Under 5 s on this repository''s open tickets: the median of five runs, measured by the CTO and recorded in the evidence. Verify: docs/changes/W2-136-evidence.md records five timed runs of gov plan on the open tickets with their median under 5 s (measured 0.81 s, 77 open tickets) [DEC-1052 basis (3)] [Verify clause added, DEC-1157 (12)]'
  failure:
  - 'Two tickets whose writes overlap planned in the same batch without an override. Verify: a planted ticket store with two tickets whose allowed paths overlap and no override: gov plan never puts them in the same batch [Verify clause added, DEC-1157 (12)]'
  - 'A plan that differs between two runs on the same tickets, or a stale plan after a ticket changed. Verify: gov plan run twice on a planted ticket store prints the same plan; a ticket changed between runs changes the plan [Verify clause added, DEC-1157 (12)]'
  - 'A file written without --ready. Verify: gov plan without --ready on a planted store writes no file (the folder is unchanged) [Verify clause added, DEC-1157 (12)]'
  - 'A lead started for a ticket outside the approved batches or with an unmet wait, without a recorded override; a refusal that does not name what it waits for. Verify: gov launch of a lead for a planted ticket outside the ready list, and one with an unmet wait, are each refused naming the ticket, path or id it waits for; with a plan_override they start and the override is logged [Verify clause added, DEC-1157 (12)]'
profile: STANDARD
sources:
- DEC-1088
- DEC-1087
- DEC-1007
- DEC-936
- DEC-899
- DEC-235
- DEC-1052
est_loc: 500
acceptance_tests:
  path: tests/acceptance/W2-136/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer; a planted ticket store and ready list in a temporary folder
track: B
list_rows: []
---
# W2-136 gov plan: the dependency map and the launch batches

The owner's DEC-1088, from DEPENDENCY-MAP-1 (`governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md`).

- **What it does:** it reads each ticket's writes (`allowed_paths`), `needs:`, `waits_on:` and `depends_on`, derives
  which tickets must wait for which, and proposes launch batches.
  - The orchestrator approves them into the ready list (DEC-1007 (2)).
  - `gov launch` refuses a lead outside the approved batches or with unmet waits (S9).
  - The machine's limits are W2-20's line (DEC-1088 (5)(b)).
- **`reads:` orders nothing.** It is wide by design, information and a warning (DEC-1088 (3)).
- **Timing:** built right after re-pin window 4, beside the experiments, tests first; live at the lift's re-pin, before
  the three layers' streams start (DEC-1088 (4)). It lands with W2-20's launch line.
- **Deps:**
  - W2-128 (the template's fields; until they land, every ticket is `NEEDS_UNDECLARED` and planned on its writes and
    `depends_on`);
  - W2-20 (the gate it lands with).
- **Est.:** about 500 lines (the derivation 150, the overlap matcher 80, the batches 70, the command and output 70, the
  launch check 60, the fields' reading 70), about 1.5 days with its tests and one review.

**TESTS-READY (built beside the experiments, DEC-1092 (5)):** `tests/acceptance/W2-136/` at `543b69540` on
`w2/W2-136-tests`: 76 cases, 66 red on integrate for the right reason, 10 green guards; the interface in their README
(the text lines, `--json`, exit codes, the `--ready` form, `plan_check.check_lead(root, ticket_id, *, ready=)`, the
launcher's lead path). S3's matcher is `gov.guard.decide._match_pattern`. **The designer's D-1 settled (CTO, delegated
under DEC-1088 (5)(a)):** `src/gov/launch/launcher.py` joins the paths for the one call to `plan_check` at the argument
checks, as S9 already states; W2-20 (built and held) holds the launcher's gate line and lands with this ticket. [DEC-1088]

**Merged (CTO, 2026-11-07):** the second pass (`992af31c`, CTO's settlements under DEC-1088 (5)(a): the launcher never
checks the calling session's `GOV_TICKET`; an admitted lead starts with `build_lead_settings`, as the dispatcher's lead
line, workers unchanged); `gov accept W2-136` 76/76 with and without the CTO's lead environment; the scoped regression
outside the sandbox 3,398 passed, 14 red, all 14 red on integrate too (D-10's list); S11 0.81 s median (`8245c1af`);
review round 1 READY by `verdict.py` (`governance/project/orchestration/reviews/w2-136.md`): **F2** (the check reads the
folder's own tickets and ready list, which can be stale; fails open once leads go through `gov launch`) is an entry
criterion of W2-20, the ticket that routes leads through it (DEC-803); F1, F3-F7 Wave 3 rows. Merged into
`w2/integrate`; live at the lift's re-pin with W2-20. Formal close at the lift. [DEC-1088]
