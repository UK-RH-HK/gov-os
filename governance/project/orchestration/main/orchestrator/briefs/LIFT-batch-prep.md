# Batches 1 to 3 after the lift: each ticket's true state, its next step, its brief, and the launch list (DEC-1126, DEC-1110 (3))

Read `LIFT-common.md` first (scratch only; you launch nothing, claim nothing, create no worktree, commit nothing).
Role: orchestration helper, Sonnet high, class C1 (DEC-1120). Scratch folder:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/batch-prep/`.

## Context
The owner approved the ready lists (`governance/project/orchestration/packages/READY-AFTER-LIFT-1.md`, batches 1 to 3)
with W2-82 at P3; usage rule (A) has ended, the 80 % brake stays (week at 64 % at 13:47, reset 11-15 09:00). Now
`gov plan --open` (the live pin) is the plan; read it fresh. The dispatcher starts only what is in
`dispatch/ready.txt` (`dispatch/README.md`: `<W2> <ticket id> <brief in ../briefs/> <log in ../log/>`; each brief
built and its readiness checked; claim committed, worktree merged before). The orchestration skill
(`template/governance/kernel/skills/orchestration/SKILL.md` or `.claude/skills/orchestration/`) and
`governance/project/prompts/w2-orchestrator.md` say how a lead is started; `governance/project/briefs/` holds the
lead brief templates (LEAD-w2-common.md and others).

Closes in flight, not yours: W2-96, W2-122, W2-123, W2-126, W2-92 (held for the owner's path-map edit), W2-112,
W2-151, W2-05 (LIFT-CLOSES-1), W2-32 and W2-15a (open at the lift). W1-01b, W2-66b, W2-90c may close on D-10's ruled
red (DEC-1126 (7)).

## For each ticket of batches 1 to 3 (fresh from `gov plan --open`), one row
1. **State, from the records:** the ticket's status, its branch(es) (`git branch -a --list 'w2/<W2>*'`), whether its
   work is merged into `w2/integrate` (`git branch --merged`), its last commit and its acceptance folder; its
   `tk`/ticket notes; DECIDED-NOT-DONE rows naming it; LIFT-CLOSES-1 if it is there.
2. **The next step,** one of: formal close (by whom, what it needs), test-design round, engineer round, review round,
   product-spec round, research run, owner's decision first, nothing (done). Name the role and the class
   (RUBRIC-2: `governance/project/orchestration/packages/RUBRIC-2-APPLY.md`, DEC-1120) and so the model and effort.
3. **The brief:** for a step that starts a lead, run `gov brief <ticket>` (the live pin; it refuses a ticket that is
   not READY, and its refusal is a finding: copy it) with its output into your folder as
   `briefs/<W2>-<step>.md`. Do not write `briefs/` in the CTO's folder.
4. **Cost:** the step's estimate in lead-hours and in percent of the week's usage, from the records of similar
   rounds (`log/usage.txt` jumps around past leads' runs; `dispatch/peaks.json`; the forecast package
   `packages/FORECAST-W2-3.md`). Say how you estimated.

## Write
`BATCH-PREP.md`: the table (ticket, state, next step, role/class/model, brief file or refusal, cost); then the order you
recommend starting them in, the critical path to EXAMIN's copy (W2-27, `DAEO-h4rh`) first; the total projected usage
for batches 1 to 3 against the 80 % brake; and the `ready.txt` lines you propose (not written to `dispatch/`). Plain
language, short. Return the twelve fields, short. Estimate 1 to 1.5 h.
