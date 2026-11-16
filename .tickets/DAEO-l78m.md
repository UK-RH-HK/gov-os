---
id: DAEO-l78m
status: in_progress
deps: []
links: []
created: 2026-10-29T15:55:51Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-81
tags: [wave-2, adoption, proving-ground, tests, full]
wbs_id: W2-81
title: 'The adoption proving ground: five synthetic repositories with planted problems, a judge, and question sets per repository'
class: test-design
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-81/w2_81_judge.py
- tests/acceptance/W2-81/test_w2_81_judge.py
- tests/acceptance/W2-81/README.md
- docs/probes/DAEO-l78m/**
kpis:
  success:
  - 'Five repositories of different shapes, built at test time, file by file and commit by commit, each in a temporary folder of its own as a git repository of its own (as W1-41''s cases build theirs): a Python application with drifted specs and plans; a Rust workspace of several crates; a TypeScript monorepo of several packages; a repository of legacy documents and large files; a repository with a secret in its history. Nothing is cloned from this repository, its worktrees or the dev tiers, and no built repository is committed; the large files are generated at test time, never tracked [DEC-941, DEC-936 item 3.6, REPLAN-W2 section 7.6] Verify: the README''s "The five shapes, and the clean variant" and the builders'' self-tests in tests/acceptance/W2-81/ (accepted at the close)'
  - 'Planted problems whose correct handling is known in advance, each kind in at least two shapes so that a shape-specific answer cannot pass: a stale spec that looks current (a current status and a recent date, contradicted by the code and by a newer spec); a superseded plan; a misleading file name (a name that says old, draft or unused on a file that is live, and one that says current on a file that is not); a secret; an orphaned test (its subject removed). The names, places and wording of each instance are drawn from a seed per run, the seed is in the report, and the list of what was planted (the manifest) is kept outside the built repository [DEC-941, DEC-936 item 3.6] Verify: the README''s "The planted problems", "The seed" and "The manifest" and their self-tests (accepted at the close)'
  - 'The correct handling of each kind is written in the README with the record that must show it, against the adoption stages as built (A0 to A6 and A8 lite, A7 and A10 lite after W2-52; CAP-44.b to CAP-44.h): the stale spec classed historical or drift flagged naming the newer source, and never cited as governing; the superseded plan linked to its successor, out of default results, never deleted; the misleading name classed by its content and references, any rename proposed as a governed batch or ticket after the A5 review, never moved by adoption on its own (CAP-44.j); the orphaned test reported as a finding naming the test and its missing subject, never deleted or silently skipped; the legacy documents classed and extracted or retired as A8 states; the large files classed and kept out of the semantic index within the budget [DEC-936 item 3.6, CAP-44.b, CAP-44.e, CAP-44.g, CAP-44.j] Verify: the README''s "The judge" and "What the judge reads, per kind", checked by test_w2_81_judge.py (accepted at the close)'
  - 'The secret is generated at test time from parts (a random value in a form the secrets scanner''s default rules detect), committed in an early commit and removed in a later one, so it lives in history only; it is never written whole in a tracked file of this repository. Correct handling: adoption finds it in history; it reports the path, a 12-digit commit and the rule only; the value is in no record, index store, log, proposal, report or output (compared in memory, never printed); a finding with a human gate stands (the rewrite or rotation is the owner''s) and the verdict cannot be ADOPTED_HEALTHY while it is open [DEC-911, CAP-03.a, CAP-03.d, CAP-44.g, CAP-44.h] Verify: the README''s "The secret, and why its value never appears" and its self-tests (accepted at the close)'
  - 'Controls against over-flagging: in each repository a current spec that looks old (an old date, "draft" in its name) and a live file under a legacy-sounding folder; and one clean variant of a shape with nothing planted. Flagging a control is mishandling, so an adoption that marks everything stale cannot pass [DEC-941] Verify: the README''s "The controls" and the judge''s control cases in test_w2_81_judge.py (accepted at the close)'
  - 'The judge: given one repository''s manifest and an adoption''s outputs on it (its stage records, path map, proposals, findings, verdict and index), it gives each planted problem FOUND_AND_HANDLED, MISSED or MISHANDLED with the evidence it read, and each control CLEAN or FLAGGED. Its verdict is READY only when every planted problem in every repository is FOUND_AND_HANDLED, no control is FLAGGED, and every question figure meets its floor. It fails closed: a missing, unreadable or malformed record is MISSED, never handled; a stage not built is NOT_BUILT and named, never passed; a judge error is an error, never READY [DEC-936 item 3.6, DEC-941] Verify: the README''s "The judge" and "NOT_BUILT versus MISSED", checked by test_w2_81_judge.py (accepted at the close)'
  - 'A question set per repository: the visible (development) half, written by this ticket, at least 10 questions per repository with their gold sources and their forbidden citations (the stale spec, the superseded plan); the hidden (measurement) half written by a separate independent auditor session (see the card) in the form this README states (its questions, and planted-problem variants the runner builds when the hidden half is present), where the path map''s evaluation_sets block refuses it to the sessions measured. The scorer reports both figures per repository, hit@5 against CAP-10''s floor of 85 and the share of questions whose stacked context holds all their evidence against the 99 % target, never one without the other; a forbidden citation in the top five counts as a miss; it prints scores and question ids only, never a hidden question or answer [DEC-833, DEC-820 (d), DEC-845, DEC-873] Verify: the README''s "The scorer", "The visible question half" and "The hidden half''s form" with their self-tests (accepted at the close)'
  - 'Mutation testing of the judge, as adoption''s own mutation check: a stand-in adoption output that handles every planted problem and flags no control is READY; for every planted problem in every repository, a stand-in that misses exactly that one is NOT_READY naming it (one killed mutant per planted problem, listed in the README); stand-ins that mishandle (the secret found but its value in a record; the misleading file moved, not proposed; the superseded plan deleted; the orphaned test deleted) and one that flags a control are NOT_READY; a scorer stand-in at 84 on hit@5, or one reporting a single figure, is NOT_READY [DEC-936 item 3.6, DEC-833] Verify: the README''s "The mutation self-tests" table, one killed mutant per row in test_w2_81_judge.py (accepted at the close)'
  - 'One command for the real run, not collected as a test: it builds the five repositories under a folder given by literal path (a temporary folder, or ~/gov-os-runs/W2-81/ by DEC-728), runs the built adoption stages and gov retrieve on each, or reads the outputs of an adoption a launched session ran there, and writes the report (per repository, per planted problem, the controls, both figures, the seed, the verdict) as JSON and markdown in that folder. It writes nothing in this repository; its first real run is the orchestrator''s, after blocks B and C [DEC-728, DEC-941] Verify: the runner w2_81_run.py''s real run by the orchestrator (report.json and report.md in the run folder; 2026-11-15 and 2026-11-16 on 0.1.0)'
  - 'Hermetic and bounded: the suite''s cases use stand-ins and need no network, no model and no adoption that works; they write only in their temporary folders and remove them; they run under 120 s alone and under the close''s parallel load; none is skipped (the skip guard''s count is unchanged), and a missing tool (git, the secrets scanner) fails naming it. Nothing in the workbench is listed or read; GOV_DEV_TIERS is not used [DEC-898, DEC-899 item 7, DEC-906] Verify: the README''s "Hermetic and bounded" and the suite''s timings and skip-guard count (accepted at the close)'
  - 'In each synthetic repository, a ticket closes with gov close at exit 0 on a pinned release (W2-16''s numbered, frozen release): the clean gov close of exit criterion 1; its real run is the orchestrator''s [DEC-953, DEC-954 Q8c] Verify: the orchestrator''s real run: gov close per repository at exit 0 on the pinned release (DEC-1197 (3): the re-run on 0.1.1 with a LITE ticket cycle)'
  - 'The builders and the per-repository question sets serve W2-88''s proof of memory for any repository, read-only; the hidden half is W2-93''s [DEC-954 Q9f, DEC-957] Verify: W2-88''s acceptance suite imports the builders and question sets read-only (accepted at W2-88''s close)'
  - line: "S-STAGES (DEC-1197 (2)) The judge counts A7 and A10 as built from the adoption command's own stage list, `gov.adopt.command.STAGES` (the list `gov adopt --lite --stage` accepts, which names A7 and A10), not from `gov.adopt.project.STAGES` (A0 to A6, A8, A9); its self-test and the README's \"Today's list\" say the same; with A7 and A10 built, a repository whose A7 or A10 record is absent or malformed is MISSED and named, never NOT_BUILT and never passed"
    verify: "tests/acceptance/W2-81/test_w2_81_judge.py: `built_today()` holds A7 and A10 exactly when `gov.adopt.command.STAGES` lists them; a stand-in adoption output without the A7 record gives A7 MISSED (not NOT_BUILT) and NOT_READY naming it; one with both lite records in the stages' front matter gives them FOUND; the README's capability table row for A7, A10 reads built, from command.STAGES"
  failure:
  - "A planted problem judged FOUND_AND_HANDLED when the adoption missed or mishandled it, or a missing or unreadable record read as handled. Verify: the mutation self-tests in test_w2_81_judge.py (a missed or unreadable record is MISSED; accepted at the close)"
  - "A READY verdict with a control flagged, a stage unmeasured, or a figure below its floor or reported alone. Verify: the mutation self-tests in test_w2_81_judge.py (a flagged control, an unmeasured stage, a figure below its floor or alone: NOT_READY)"
  - "The secret's value written whole in any tracked file, record, log, report or output. Verify: the secret's self-tests (the value compared in memory, never printed; accepted at the close)"
  - "A hidden question or answer printed, logged or written outside the hidden half. Verify: the scorer's and the hidden half's self-tests (scores and ids only; accepted at the close)"
  - "A case that writes in this repository, reads the workbench, needs the network or is skipped. Verify: the README's \"Hermetic and bounded\" and the skip guard (accepted at the close)"
non_goals:
- no change to the builders, the planted problems, the scorer, the runner or either question half (DEC-1197 (2) reopens the stage list only)
- the hidden half is neither read nor written
- the full re-run on 0.1.1 is the orchestrator's (DEC-1197 (3)), not this reopen's
profile: FULL
sources:
- DEC-941
- DEC-936
- DEC-930
- DEC-833
- DEC-820
- DEC-845
- DEC-873
- DEC-911
- DEC-728
- DEC-899
- DEC-953
- DEC-954
- DEC-957
- CAP-03.a
- CAP-03.d
- CAP-44.b
- CAP-44.e
- CAP-44.g
- CAP-44.h
- CAP-44.j
- DEC-898
- DEC-906
est_loc: 1200
acceptance_tests:
  path: tests/acceptance/W2-81/
  author: independent-test-designer (MR-3); the proving ground is the deliverable (builders, planted problems, judge, scorer, the visible question half and the judge's self-tests); the hidden question half by a separate independent auditor session
track: B
list_rows: []
---
# W2-81 The adoption proving ground: five synthetic repositories with planted problems, a judge, and question sets per repository

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-81), from the re-plan package's §7.6 and the owner's addition of 2026-10-29 (DEC-941; DEC-936 item 3.6; DEC-930).

- **Why:** passing the proving ground becomes an entry criterion for EXAMIN's copy, beside the memory measure (DEC-936 item 3.6). Adoption must find and handle each planted problem; a planted problem that passes unnoticed means adoption is not ready. Today nothing measures whether adoption tells current from historical, keeps secrets out of its indexes, or proposes restructuring rather than doing it.
- **Place:** block E of the re-plan (§2.1). The ticket is test code only and shares no path with a ticket in flight, so it starts in a free slot now. Its first real run is the orchestrator's, after blocks B (memory) and C (K3). The planted problems it finds missed decide what W2-26, W2-52 and W2-27 to W2-30 must cover.
- **Paths:** builders, manifest, judge, scorer, runner, the visible question half and the README, all under `tests/acceptance/W2-81/`. Only files named `test_*.py` are the judge's self-tests. The runner and builders are support modules that the regression does not collect. The built repositories exist only in temporary folders or under the run folder.
- **Not in this ticket:** the hidden question half, which a separate independent auditor session writes (see the card's companion). The path map's `evaluation_sets` entry for it is the orchestrator's: the path map is shared core, so it goes in a gap between queues (DEC-929 item 2). The real run and its report are also outside this ticket.

## Reopened 2026-11-16 by the owner (DEC-1197 (2), P-W2-81-VERDICT-1 (b))

W2-81's full run on release 0.1.0 (seed 1324021) gave A7 and A10 NOT_BUILT in all six repositories although the product
built them: the judge reads `gov.adopt.project.STAGES` (`w2_81_judge.py` `built_today`, lines 135-141), which lists A0
to A6, A8 and A9, while the product lists A7 and A10 in `gov.adopt.command.STAGES`, and its lite gates wrote exactly the
records the judge looks for (`governance/adoption/A7-independent-migration-verification.md`,
`A10-independent-memory-verification.md`). S-STAGES fixes the judge within its purpose. It is W2-81's own test code, so a
test designer's change (the role this ticket always had); the allowed paths are narrowed to the judge, its self-test,
the README and the narrow check's record (they were `tests/acceptance/W2-81/**`). The twelve success and five failure lines of 2026-10-29 predate the verify form and `gov brief` refuses them (`KPI_NO_VERIFY`); the CTO appended to each a Verify clause naming the README section and the self-tests or run that already check it, and changed no line's text (listed for the owner's reading). FULL: a narrow independent check
(DEC-1154) before the land. The full re-run on 0.1.1 (DEC-1197 (3)) is the orchestrator's, after the re-pin.

