# Lead brief: D1, the lite adoption verdict stage (CAP-44.h), a new feature ticket W2-210

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `d1-verdict`; worktree
`/home/usain/gov-os-worktrees/E2-d1-verdict`, branch `e2/d1-verdict` from `w2/integrate`. **Do not merge.** It rides
release 0.1.6 (DEC-1231); it must be built and green on its branch by tomorrow, 2026-11-23. Every helper Sonnet (DEC-1225).

**The decisions:** DEC-1227 D1 (a) "build the lite verdict stage (CAP-44.h)"; DEC-1231 "the verdict stage rides in the
next release, after 0.1.5". Read `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` rows R7, `VERDICT`, A5 and D1:
the record type exists (`adoption-verdict`, W2-02, DAEO-zflj) but no stage or command writes or checks it
(`command.STAGES` = A0, A1, A2, AS, A3 to A10, MA); W2-81's judge counts every stage not PRESENT as a reason, so six
reasons in the 0.1.4 run were the missing verdict. Read CAP-44.h whole in `docs/contract/CONTRACT_v5.md` (about line 709).

## Step 1: the ticket (you write it; the CTO approves its KPI lines by this brief)
Create `.tickets/` entry W2-210 (`tk` or the form of other feature tickets: `wbs_id: W2-210`, `closes: [CAP-44.h]`,
sources DEC-1227, DEC-1231, CAP-44.h, DAEO-zflj, DAEO-l78m), kind feature, with a short spec and these KPI lines (each
with its verify; refine the wording, keep the substance):
- **V1** `gov adopt --lite --stage VERDICT` (a stage after the last lite stage; it is in `command.STAGES`) computes every
  lite condition of CAP-44.h by code from the repository: A0 to A6 and A8 with their stage records and the A5 review; the
  native layout kept; the lite A7 and A10 gates passed; the pinned, hash-verified release (`gov doctor` MATCH); `gov
  doctor` exit 0; `gov check` with no RED family; one ticket closed through the landing at exit 0 with the repository's
  own test command. Each condition is recorded met / not met with its evidence (command, exit, path).
- **V2** The verdict: ADOPTED_HEALTHY when every lite condition is met; ADOPTED_WITH_ACCEPTED_EXCEPTIONS when each
  condition not met is accepted by name in an owner decision (a commit with `Role: owner`, or the owner's exceptions file
  the W2-81 runner already reads; say which and why); otherwise NOT_ADOPTED_HEALTHY. Only the owner accepts an exception.
- **V3** The record (`adoption-verdict`, schema of W2-02, unchanged unless it cannot carry V1) names itself lite, lists
  the ten ADOPTED_HEALTHY conditions of CAP-44.h with each one's W2 / W3 / lite-part marking, and names the conditions
  it does not check.
- **V4** The independent part: CAP-44.h says "from a fresh Independent Auditor". The stage's code computes; a fresh
  `independent-auditor` session (Sonnet) confirms the record against the repository, or the record is computed
  deterministically and the auditor's confirmation is a recorded step: choose the simpler that keeps the verdict by code,
  and state it in one line in your return.
- **V5** W2-81's judge reads the verdict stage as PRESENT when its record exists and is well formed (its six reasons
  go); a missing or malformed record stays a reason.
- Failure lines: a hand-written verdict record not produced by the stage is refused; ADOPTED_HEALTHY with any condition
  not met is impossible; an exception accepted by anyone but the owner is refused.

## Step 2: the flow
Test designer (Sonnet) writes `tests/acceptance/W2-210/`, red on the base, README map; engineer (Sonnet) until
`gov accept W2-210` is green; synthetic adopted repositories under `~/gov-os-runs/d1/` for the real-repository cases.

## Green and return
`gov accept W2-210`, `tests/unit/adopt`, W1-41, W2-02, W2-52, W2-192, `tests/acceptance/W2-81` (the judge),
`tests/unit/optin`. Return: branch and head; V1 to V5 with tests; V4's choice in one line; the trial figures (runs to
green, send-backs, minutes, cost); reds not yours.
