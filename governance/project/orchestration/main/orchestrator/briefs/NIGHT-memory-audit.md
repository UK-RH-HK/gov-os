# Anti-drift audit (e, part 2): the memory audit as a scheduled tool, for the owner's approval (DEC-1125 (2), (3) (iii) e)

Read `NIGHT-common.md` first. Role: product-spec helper, Sonnet high, class C2.

## The decision
DEC-1101 (read it whole in the register) as changed by DEC-1125 (2): memory quality is audited **weekly while
development is active, monthly once stable**, a scheduled practice like the nightly, built as a tool for Gov OS and
every adopted repository: an independent writer drafts fresh questions, they are measured once, misses are classified,
drift is fixed. It replaces ad-hoc re-measures (DEC-1097 (4) folds into it). DEC-1101 (2)-(3): automated independent
sessions in walled folders, fixed briefs the owner approves once (hashed; the CTO never changes them), content chosen
by rule (git changes since the last audit plus a seeded sample), memory's own search and run outputs denied to them.

## The task
1. **Its state today**, with evidence: W2-149 (`DAEO-52ku`, the independent sessions' launch script) and its merge
   (row 86), ACT-INDEP-WALLS-1 and ACT-W2-149-INSTALL-1 (applied or waiting?), set-up A, the existing fixed briefs for
   any independent job (find them: `indep-briefs`, W2-149's tree, `governance/project/briefs/`), the measure's tool
   (W2-61's measure and what DEC-1097 used), W2-88 (adopted repositories), the nightly's scheduling (how the nightly
   is scheduled: crontab line, `nightly.sh`). Read; never run a measure, never open the evaluation sets, run folders or
   hidden halves.
2. **The fixed briefs, drafts for the owner's approval:** writer, checker, auditor (and labeller if the process needs
   one; say why). Each: purpose, inputs by rule (what it may read; how the content is chosen: the git range since the
   last audit, the seed recorded before writing, the sample size), what it must not read (and which wall enforces
   it), its output's form, the set size per audit, its stop rule, its model and effort under RUBRIC-2 (DEC-1120). Put
   them under `governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/` as drafts; their hashes are taken
   only once the owner approves.
3. **The schedule:** weekly, the day and hour (avoid the nightly's window and the owner's digests; give your reason),
   how it is run (a cron line as a proposed ACT for the owner's operator: the crontab is class (O)), how "active" and
   "stable" are told apart (a rule), and how a retrieval change waits for the next audit.
4. **Home tickets:** Gov OS (a ticket for the scheduled tool; file it with `tk create` in the form of
   `.tickets/DAEO-ar89.md`, WBS ids **W2-170 to W2-179** only) and W2-88's lines for adopted repositories (propose the
   KPI lines; do not edit W2-88's ticket, another helper audits tickets tonight).
5. **The first audit's date:** after the re-pin (the owner re-pins about 09:00-10:00 UTC 11-11), and it measures the
   re-pin's retrieval change; what must land first (the walls ACT, W2-149's install, the briefs' approval), with
   dates and the cost per audit (tokens, GPU minutes, the owner's minutes).

## Write
`governance/project/orchestration/packages/MEMORY-AUDIT-1.md` (the package for the owner: state, the briefs to
approve, the schedule, the home tickets, the first date, costs, options with your recommendation) and
`packages/MEMORY-AUDIT-1/**`; new ticket files W2-170 to W2-179. Nothing else.

## Return
The twelve fields, short: the state in five lines, the briefs drafted, the schedule, the tickets filed, the first
audit's date and what it waits on, the costs. Estimate 1.5-2 h.
